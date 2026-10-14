import argparse
import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import ijson
import pyarrow as pa
import pyarrow.parquet as pq

FIELDS = {
    "session": [
        ["session_id", "STRING"],
        ["creation_date", "DATETIME"],
        ["mfa_authenticated", "BOOLEAN"],
        ["additional_info", "STRING"],
        ["identity_id", "STRING"],
    ],
    "identity": [
        ["identity_id", "STRING"],
        ["type", "STRING"],
        ["principal_id", "STRING"],
        ["arn", "STRING"],
        ["user_name", "STRING"],
        ["account_id", "STRING"],
    ],
    "event": [
        ["event_id", "STRING"],
        ["event_time", "DATETIME"],
        ["event_source", "STRING"],
        ["event_name", "STRING"],
        ["source_ip", "STRING"],
        ["user_agent", "STRING"],
        ["request_params", "STRING"],
        ["response_params", "STRING"],
        ["identity_id", "STRING"],
        ["session_id", "STRING"],
        ["account_id", "STRING"],
    ],
    "account": [
        ["account_id", "STRING"],
        ["account_alias", "STRING"],
        ["email", "STRING"],
        ["phone", "STRING"],
    ],
    "eventresource": [
        ["event_id", "STRING"],
        ["resource_id", "STRING"],
        ["pre_state", "STRING"],
        ["post_state", "STRING"],
    ],
    "resource": [
        ["resource_id", "STRING"],
        ["resource_name", "STRING"],
        ["resource_type", "STRING"],
        ["additional_metadata", "STRING"],
    ],
}
TABLE_NAMES = ("Account", "Identity", "Session", "Event", "Resource", "EventResource")
TYPES = {"STRING": pa.string(), "DATETIME": pa.timestamp("us"), "BOOLEAN": pa.bool_()}
SCHEMAS = {
    name: pa.schema([(field, TYPES[kind]) for field, kind in FIELDS[name.lower()]])
    for name in TABLE_NAMES
}


def stable_id(*parts):
    return hashlib.sha256(json.dumps(parts).encode()).hexdigest()


def timestamp(value):
    if not value:
        return None
    return (
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        .astimezone(timezone.utc)
        .replace(tzinfo=None)
    )


def encoded(value):
    return json.dumps(value or {}, sort_keys=True, default=str)


def resources(record):
    for resource in record.get("resources") or []:
        arn = resource.get("ARN") or resource.get("arn")
        if arn:
            yield arn, resource.get("type") or "AWSResource", resource, "", ""
    request = record.get("requestParameters") or {}
    response = record.get("responseElements") or {}
    account = str(
        record.get("recipientAccountId")
        or (record.get("userIdentity") or {}).get("accountId")
        or ""
    )
    region = record.get("awsRegion") or ""
    partition = ((record.get("userIdentity") or {}).get("arn") or "arn:aws:").split(
        ":"
    )[1]
    if request.get("bucketName"):
        yield (
            f"arn:{partition}:s3:::{request['bucketName']}",
            "AWS::S3::Bucket",
            {},
            "",
            "",
        )
    for source in (request, response):
        for item in (source.get("instancesSet") or {}).get("items") or []:
            if item.get("instanceId"):
                arn = f"arn:{partition}:ec2:{region}:{account}:instance/{item['instanceId']}"
                yield (
                    arn,
                    "AWS::EC2::Instance",
                    item,
                    (item.get("previousState") or {}).get("name", ""),
                    (item.get("currentState") or {}).get("name", ""),
                )
    for key, kind, service, prefix in (
        ("roleName", "AWS::IAM::Role", "iam", "role/"),
        ("functionName", "AWS::Lambda::Function", "lambda", "function:"),
        ("name", "AWS::CloudTrail::Trail", "cloudtrail", "trail/"),
    ):
        name = request.get(key)
        if not name or record.get("eventSource") != f"{service}.amazonaws.com":
            continue
        resource_region = "" if service == "iam" else region
        arn = (
            name
            if name.startswith("arn:")
            else f"arn:{partition}:{service}:{resource_region}:{account}:{prefix}{name}"
        )
        yield arn, kind, {}, "", ""


def records_from_stream(stream, compressed=False):
    if compressed:
        with gzip.GzipFile(fileobj=stream) as decoded:
            yield from ijson.items(decoded, "Records.item")
    else:
        yield from ijson.items(stream, "Records.item")


def records_from_path(input_path):
    path = Path(input_path)
    files = (
        [path]
        if path.is_file()
        else sorted(
            p for p in path.rglob("*") if p.name.endswith((".json", ".json.gz"))
        )
    )
    for file in files:
        with file.open("rb") as stream:
            yield from records_from_stream(stream, file.name.endswith(".gz"))


def convert(input_path):
    rows = {name: {} for name in SCHEMAS}
    skipped = 0
    for record in records_from_path(input_path):
        event_id = record.get("eventID")
        if not event_id:
            raise ValueError(f"Record without eventID in {input_path}")
        if event_id in rows["Event"]:
            continue
        identity = record.get("userIdentity") or {}
        account_id = str(identity.get("accountId") or "")
        identity_id = identity.get("arn") or ""
        if account_id:
            rows["Account"][account_id] = dict(
                account_id=account_id, account_alias="", email="", phone=""
            )
        if identity_id:
            rows["Identity"][identity_id] = dict(
                identity_id=identity_id,
                type=identity.get("type"),
                principal_id=identity.get("principalId"),
                arn=identity_id,
                user_name=identity.get("userName"),
                account_id=account_id or None,
            )
        context = identity.get("sessionContext") or {}
        attributes = context.get("attributes") or {}
        creation = timestamp(attributes.get("creationDate"))
        session_id = None
        if identity_id and creation:
            session_id = stable_id(identity_id, attributes["creationDate"])
            mfa = {"true": True, "false": False}.get(
                str(attributes.get("mfaAuthenticated")).lower()
            )
            rows["Session"][session_id] = dict(
                session_id=session_id,
                identity_id=identity_id,
                creation_date=creation,
                mfa_authenticated=mfa,
                additional_info=encoded(context),
            )
        else:
            skipped += 1
        rows["Event"][event_id] = dict(
            event_id=event_id,
            event_time=timestamp(record.get("eventTime")),
            event_source=record.get("eventSource"),
            event_name=record.get("eventName"),
            source_ip=record.get("sourceIPAddress"),
            user_agent=record.get("userAgent"),
            request_params=encoded(record.get("requestParameters")),
            response_params=encoded(record.get("responseElements")),
            identity_id=identity_id or None,
            session_id=session_id,
            account_id=account_id or None,
        )
        for arn, kind, metadata, before, after in resources(record):
            resource_id = stable_id(arn)
            rows["Resource"].setdefault(
                resource_id,
                dict(
                    resource_id=resource_id,
                    resource_name=arn,
                    resource_type=kind,
                    additional_metadata=encoded(metadata),
                ),
            )
            key = (event_id, resource_id)
            edge = rows["EventResource"].setdefault(
                key,
                dict(
                    event_id=event_id,
                    resource_id=resource_id,
                    pre_state="",
                    post_state="",
                ),
            )
            if before or after:
                edge.update(pre_state=before, post_state=after)
    if not rows["Event"]:
        raise ValueError("No CloudTrail Records found")
    for name, records in rows.items():
        print(f"{name}: {len(records)} rows")
    print(f"Events without observed session context: {skipped}")
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = convert(args.input)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, schema in SCHEMAS.items():
        data = pa.Table.from_pylist(list(rows.pop(name).values()), schema=schema)
        pq.write_table(data, args.output / f"{name}.parquet")
