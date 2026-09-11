#!/usr/bin/env python3
"""Load the flaws.cloud CloudTrail archive into Delta tables in Microsoft Fabric.

Run this file from a Fabric notebook that is attached to a schema-enabled
lakehouse. Install ijson in the notebook first with: %pip install ijson
"""

import gzip
import hashlib
import io
import json
import tarfile
import uuid
from datetime import datetime

import ijson
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    BooleanType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

ARCHIVE_PATH = "/lakehouse/default/Files/cloudtrail_raw/flaws_cloudtrail_logs.tar"
DATABASE = "security_graph"
BATCH_SIZE = 100_000


TABLE_SCHEMAS = {
    "account": StructType([
        StructField("account_id", StringType(), False),
        StructField("account_alias", StringType(), True),
        StructField("email", StringType(), True),
        StructField("phone", StringType(), True),
    ]),
    "identity": StructType([
        StructField("identity_id", StringType(), False),
        StructField("type", StringType(), True),
        StructField("principal_id", StringType(), True),
        StructField("arn", StringType(), True),
        StructField("user_name", StringType(), True),
        StructField("account_id", StringType(), True),
    ]),
    "session": StructType([
        StructField("session_id", StringType(), False),
        StructField("creation_date", TimestampType(), True),
        StructField("mfa_authenticated", BooleanType(), True),
        StructField("additional_info", StringType(), True),
        StructField("identity_id", StringType(), True),
    ]),
    "event": StructType([
        StructField("event_id", StringType(), False),
        StructField("event_time", TimestampType(), True),
        StructField("event_source", StringType(), True),
        StructField("event_name", StringType(), True),
        StructField("source_ip", StringType(), True),
        StructField("user_agent", StringType(), True),
        StructField("request_params", StringType(), True),
        StructField("response_params", StringType(), True),
        StructField("identity_id", StringType(), True),
        StructField("session_id", StringType(), True),
        StructField("account_id", StringType(), True),
    ]),
    "resource": StructType([
        StructField("resource_id", StringType(), False),
        StructField("resource_name", StringType(), True),
        StructField("resource_type", StringType(), True),
        StructField("additional_metadata", StringType(), True),
    ]),
    "eventresource": StructType([
        StructField("event_id", StringType(), False),
        StructField("resource_id", StringType(), False),
        StructField("pre_state", StringType(), True),
        StructField("post_state", StringType(), True),
    ]),
}


def safe_get(data, key, default=""):
    if not data:
        return default
    value = data.get(key)
    return default if value is None else value


def json_string(value):
    return json.dumps(value, ensure_ascii=False, default=str) if value is not None else ""


def parse_timestamp(value):
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def synthetic_account_details(account_id):
    """Create stable synthetic profile values without introducing real PII."""
    digest = hashlib.sha256(account_id.encode("utf-8")).hexdigest()
    return {
        "account_alias": f"account-{digest[:8]}",
        "email": f"account-{digest[:8]}@example.invalid",
        "phone": f"+1-555-{int(digest[8:12], 16) % 10000:04d}",
    }


def infer_resource_type(params):
    if not params:
        return ""
    if "trailNameList" in params or (
        "name" in params
        and ("s3BucketName" in params or "enableLogFileValidation" in params)
    ):
        return "cloudtrailtrail"
    if "bucketName" in params and any(
        key in params
        for key in (
            "CreateBucketConfiguration", "bucketPolicy", "logging", "replication",
            "website", "acl", "tagging", "versioning", "policy"
        )
    ):
        return "s3bucket"
    checks = (
        (("instancesSet", "instanceId"), "ec2instance"),
        (("imagesSet", "imageId"), "ami"),
        (("volumeSet", "volumeId"), "volume"),
        (("snapshotSet", "snapshotId"), "snapshot"),
        (("availabilityZoneSet",), "availabilityzone"),
        (("securityGroupSet", "securityGroupIdSet", "ipPermissions"), "securitygroup"),
        (("subnetSet", "subnetId"), "subnet"),
        (("vpcSet", "vpcId"), "vpc"),
        (("instanceProfileName",), "iaminstanceprofile"),
        (("restApiId",), "apigateway"),
        (("stackStatusFilter",), "cloudformationstack"),
        (("configurationRecorder", "deliveryChannel"), "awsconfig"),
        (("customerGatewaySet",), "customergateway"),
        (("dhcpOptionsSet",), "dhcptoptions"),
        (("networkAclIdSet",), "networkacl"),
        (("reservedInstancesSet", "spotInstanceRequestIdSet"), "reservedorspotinstances"),
        (("repositoryNames",), "codecommit"),
        (("certificateStatuses",), "acmcertificate"),
        (("virtualMFADeviceName", "serialNumber"), "mfadevice"),
        (("maxResults", "nextToken", "filterSet", "pageSize", "limit"), "genericquery"),
    )
    for keys, resource_type in checks:
        if any(key in params for key in keys):
            return resource_type
    if "roleName" in params and (
        "assumeRolePolicyDocument" in params or "policyDocument" in params
    ):
        return "iamrole"
    if "policyName" in params or "policyArn" in params:
        return "iampolicy"
    if "functionName" in params and "handler" in params:
        return "lambdafunction"
    return ""


def create_tables(spark):
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {DATABASE}")
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {DATABASE}.account (
        account_id STRING, account_alias STRING, email STRING, phone STRING
    ) USING DELTA""")
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {DATABASE}.identity (
        identity_id STRING, type STRING, principal_id STRING, arn STRING,
        user_name STRING, account_id STRING
    ) USING DELTA""")
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {DATABASE}.session (
        session_id STRING, creation_date TIMESTAMP, mfa_authenticated BOOLEAN,
        additional_info STRING, identity_id STRING
    ) USING DELTA""")
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {DATABASE}.event (
        event_id STRING, event_time TIMESTAMP, event_source STRING, event_name STRING,
        source_ip STRING, user_agent STRING, request_params STRING,
        response_params STRING, identity_id STRING, session_id STRING, account_id STRING
    ) USING DELTA""")
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {DATABASE}.resource (
        resource_id STRING, resource_name STRING, resource_type STRING,
        additional_metadata STRING
    ) USING DELTA""")
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {DATABASE}.eventresource (
        event_id STRING, resource_id STRING, pre_state STRING, post_state STRING
    ) USING DELTA""")


def reset_tables(spark):
    for table in TABLE_SCHEMAS:
        spark.sql(f"TRUNCATE TABLE {DATABASE}.{table}")


def append_rows(spark, table, rows):
    if not rows:
        return
    dataframe = spark.createDataFrame(rows, TABLE_SCHEMAS[table])
    dataframe.write.format("delta").mode("append").saveAsTable(f"{DATABASE}.{table}")
    rows.clear()


def flush_large_buffers(spark, buffers):
    for table, rows in buffers.items():
        if len(rows) >= BATCH_SIZE:
            append_rows(spark, table, rows)


def record_streams(archive_path):
    with tarfile.open(archive_path, "r:*") as archive:
        members = [
            member for member in archive.getmembers()
            if member.isfile() and member.name.lower().endswith((".json", ".json.gz"))
        ]
        print(f"Found {len(members)} CloudTrail files in {archive_path}")
        for number, member in enumerate(members, start=1):
            raw = archive.extractfile(member)
            if raw is None:
                continue
            binary = gzip.GzipFile(fileobj=raw) if member.name.lower().endswith(".gz") else raw
            text = io.TextIOWrapper(binary, encoding="utf-8")
            print(f"Processing {number}/{len(members)}: {member.name}")
            try:
                yield from ijson.items(text, "Records.item")
            finally:
                text.close()


def load_data(spark):
    buffers = {table: [] for table in TABLE_SCHEMAS}
    seen_accounts = set()
    seen_identities = set()
    seen_sessions = set()
    resource_ids = {}

    for record in record_streams(ARCHIVE_PATH):
        user_identity = record.get("userIdentity") or {}
        account_id = str(safe_get(user_identity, "accountId"))
        identity_id = str(safe_get(user_identity, "arn"))

        if account_id and account_id not in seen_accounts:
            seen_accounts.add(account_id)
            details = synthetic_account_details(account_id)
            buffers["account"].append({"account_id": account_id, **details})

        if identity_id and identity_id not in seen_identities:
            seen_identities.add(identity_id)
            buffers["identity"].append({
                "identity_id": identity_id,
                "type": str(safe_get(user_identity, "type")),
                "principal_id": str(safe_get(user_identity, "principalId")),
                "arn": identity_id,
                "user_name": str(safe_get(user_identity, "userName")),
                "account_id": account_id,
            })

        session_context = user_identity.get("sessionContext") or {}
        attributes = session_context.get("attributes") or {}
        creation_date = str(safe_get(attributes, "creationDate"))
        session_id = f"{identity_id}_{creation_date}" if identity_id and creation_date else ""
        if session_id and session_id not in seen_sessions:
            seen_sessions.add(session_id)
            buffers["session"].append({
                "session_id": session_id,
                "creation_date": parse_timestamp(creation_date),
                "mfa_authenticated": str(safe_get(attributes, "mfaAuthenticated", "false")).lower() == "true",
                "additional_info": json_string({
                    "sessionIssuer": session_context.get("sessionIssuer", {}),
                    "webIdFederationData": session_context.get("webIdFederationData", {}),
                }),
                "identity_id": identity_id,
            })

        event_id = str(safe_get(record, "eventID"))
        if not event_id:
            continue
        request_params = record.get("requestParameters") or {}
        response_params = record.get("responseElements") or {}
        buffers["event"].append({
            "event_id": event_id,
            "event_time": parse_timestamp(safe_get(record, "eventTime")),
            "event_source": str(safe_get(record, "eventSource")),
            "event_name": str(safe_get(record, "eventName")),
            "source_ip": str(safe_get(record, "sourceIPAddress")),
            "user_agent": str(safe_get(record, "userAgent")),
            "request_params": json_string(request_params),
            "response_params": json_string(response_params),
            "identity_id": identity_id,
            "session_id": session_id,
            "account_id": account_id,
        })

        candidates = []
        instances = (response_params.get("instancesSet") or {}).get("items") or []
        for item in instances:
            name = str(safe_get(item, "instanceId"))
            if name:
                candidates.append((name, "ec2instance", item,
                                   str(safe_get(item.get("previousState"), "name")),
                                   str(safe_get(item.get("currentState"), "name"))))

        inferred_type = infer_resource_type(request_params)
        inferred_name = next(
            (str(safe_get(request_params, key)) for key in ("name", "bucketName", "instanceId")
             if safe_get(request_params, key)),
            "",
        )
        if inferred_type and inferred_name:
            candidates.append((inferred_name, inferred_type, {}, "", ""))

        for name, resource_type, metadata, pre_state, post_state in candidates:
            resource_key = (resource_type, name)
            resource_id = resource_ids.get(resource_key)
            if resource_id is None:
                resource_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"cloudtrail-resource:{resource_type}:{name}"))
                resource_ids[resource_key] = resource_id
                buffers["resource"].append({
                    "resource_id": resource_id,
                    "resource_name": name,
                    "resource_type": resource_type,
                    "additional_metadata": json_string(metadata),
                })
            buffers["eventresource"].append({
                "event_id": event_id,
                "resource_id": resource_id,
                "pre_state": pre_state,
                "post_state": post_state,
            })

        flush_large_buffers(spark, buffers)

    for table, rows in buffers.items():
        append_rows(spark, table, rows)


def show_counts(spark):
    print("Loaded rows:")
    for table in TABLE_SCHEMAS:
        count = spark.table(f"{DATABASE}.{table}").count()
        print(f"  {DATABASE}.{table}: {count:,}")


def main():
    spark = SparkSession.builder.appName("CloudTrailToOneLake").getOrCreate()
    create_tables(spark)
    reset_tables(spark)
    load_data(spark)
    show_counts(spark)
    print("CloudTrail data is available as Delta tables in OneLake.")


if __name__ == "__main__":
    main()

