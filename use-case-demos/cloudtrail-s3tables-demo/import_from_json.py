#!/usr/bin/env python3
import argparse
import json
import os
import uuid

import ijson
from faker import Faker
from pyspark.sql import SparkSession

# Initialize Faker for generating sample account details
fake = Faker()


def generate_session_id(identity_id, creation_date):
  # Generate a simple session_id by concatenating identity_id and creation_date
  return f"{identity_id}_{creation_date}"


def generate_resource_id():
  # Generate a random UUID as resource_id
  return str(uuid.uuid4())


def safe_json_dumps(data):
  # Convert data to JSON string; use default=str to handle non-serializable types
  return json.dumps(data, ensure_ascii=False, default=str) if data is not None else ""


def safe_get(data, key, default=''):
  # Safely get a value from a dictionary; return default if key is missing or value is None
  if data is None:
    return default
  return data.get(key) or default


def infer_resource_type(request_params):
  # Infer resource type based on keys in requestParameters; return a tuple: (resource_type, extra_metadata)
  if not request_params:
    return '', {}
  if 'trailNameList' in request_params or ('name' in request_params and (
          's3BucketName' in request_params or 'enableLogFileValidation' in request_params)):
    return 'cloudtrailtrail', {}
  if 'bucketName' in request_params and (
          'CreateBucketConfiguration' in request_params or
          'bucketPolicy' in request_params or
          'logging' in request_params or
          'replication' in request_params or
          'website' in request_params or
          'acl' in request_params or
          'tagging' in request_params or
          'versioning' in request_params or
          ('policy' in request_params and isinstance(request_params.get('policy'), list))):
    return 's3bucket', {}
  if 'instancesSet' in request_params:
    return 'ec2instance', {}
  if 'imagesSet' in request_params or (
          'imageId' in request_params and request_params.get('imageId', '').startswith('ami-')):
    return 'ami', {}
  if 'volumeSet' in request_params or 'volumeId' in request_params:
    return 'volume', {}
  if 'snapshotSet' in request_params or 'snapshotId' in request_params:
    return 'snapshot', {}
  if 'availabilityZoneSet' in request_params:
    return 'availabilityzone', {}
  if 'securityGroupSet' in request_params or 'securityGroupIdSet' in request_params or 'ipPermissions' in request_params:
    return 'securitygroup', {}
  if 'subnetSet' in request_params or 'subnetId' in request_params:
    return 'subnet', {}
  if 'vpcSet' in request_params or 'vpcId' in request_params:
    return 'vpc', {}
  if 'roleName' in request_params and (
          'assumeRolePolicyDocument' in request_params or 'policyDocument' in request_params):
    return 'iamrole', {}
  if 'policyName' in request_params or 'policyArn' in request_params:
    return 'iampolicy', {}
  if 'instanceProfileName' in request_params:
    return 'iaminstanceprofile', {}
  if 'functionName' in request_params and 'handler' in request_params:
    return 'lambdafunction', {}
  if 'restApiId' in request_params:
    return 'apigateway', {}
  if 'stackStatusFilter' in request_params:
    return 'cloudformationstack', {}
  if 'configurationRecorder' in request_params or 'deliveryChannel' in request_params:
    return 'awsconfig', {}
  if 'customerGatewaySet' in request_params:
    return 'customergateway', {}
  if 'dhcpOptionsSet' in request_params:
    return 'dhcptoptions', {}
  if 'networkAclIdSet' in request_params:
    return 'networkacl', {}
  if 'reservedInstancesSet' in request_params or 'spotInstanceRequestIdSet' in request_params:
    return 'reservedorspotinstances', {}
  if 'repositoryNames' in request_params:
    return 'codecommit', {}
  if 'certificateStatuses' in request_params:
    return 'acmcertificate', {}
  if 'virtualMFADeviceName' in request_params or 'serialNumber' in request_params:
    return 'mfadevice', {}
  if any(k in request_params for k in ['maxResults', 'nextToken', 'filterSet', 'pageSize', 'limit']):
    return 'genericquery', {}
  return '', {}


def process_files(input_folder):
  """
  Process all JSON files in the input folder, extract data for each table,
  and return six lists corresponding to account, identity, session, event, resource, and eventresource.
  """
  accounts_rows = []
  identity_rows = []
  session_rows = []
  event_rows = []
  resource_rows = []
  event_resource_rows = []

  accounts_set = set()
  identities_set = set()
  sessions_set = set()
  resources_set = set()

  json_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.json')]
  total_files = len(json_files)
  print(f"Found {total_files} JSON file(s) in {input_folder}.")

  for json_file in json_files:
    file_path = os.path.join(input_folder, json_file)
    print(f"Processing file: {file_path}")
    try:
      with open(file_path, 'r', encoding='utf-8') as f:
        for record in ijson.items(f, "Records.item"):
          # Process account table
          user_identity = record.get("userIdentity") or {}
          account_id = safe_get(user_identity, "accountId")
          if account_id and account_id not in accounts_set:
            accounts_set.add(account_id)
            accounts_rows.append({
              "account_id": str(account_id),
              "account_alias": fake.user_name(),
              "email": fake.email(),
              "phone": fake.phone_number()
            })

          # Process identity table
          identity_id = safe_get(user_identity, "arn")
          if identity_id and identity_id not in identities_set:
            identities_set.add(identity_id)
            identity_rows.append({
              "identity_id": identity_id,
              "type": safe_get(user_identity, "type"),
              "principal_id": safe_get(user_identity, "principalId"),
              "arn": identity_id,
              "user_name": safe_get(user_identity, "userName"),
              "account_id": str(account_id)
            })

          # Process session table
          session_context = record.get("userIdentity", {}).get("sessionContext", {}) or {}
          attributes = session_context.get("attributes", {}) or {}
          creation_date = safe_get(attributes, "creationDate")
          if creation_date:
            session_id = generate_session_id(identity_id, creation_date)
            if session_id not in sessions_set:
              sessions_set.add(session_id)
              additional_info = {
                "sessionIssuer": session_context.get("sessionIssuer", {}),
                "webIdFederationData": session_context.get("webIdFederationData", {})
              }
              session_rows.append({
                "session_id": session_id,
                "creation_date": creation_date,
                "mfa_authenticated": str(safe_get(attributes, "mfaAuthenticated", "false")).lower() == "true",
                "additional_info": safe_json_dumps(additional_info),
                "identity_id": identity_id
              })
          else:
            session_id = ""

          # Process event table
          event_id = safe_get(record, "eventID")
          event_time = safe_get(record, "eventTime")
          event_source = safe_get(record, "eventSource")
          event_name = safe_get(record, "eventName")
          source_ip = safe_get(record, "sourceIPAddress")
          user_agent = safe_get(record, "userAgent")
          request_params_raw = record.get("requestParameters") or {}
          response_params_raw = record.get("responseElements") or {}
          event_rows.append({
            "event_id": event_id,
            "event_time": event_time,
            "event_source": event_source,
            "event_name": event_name,
            "source_ip": source_ip,
            "user_agent": user_agent,
            "request_params": safe_json_dumps(request_params_raw),
            "response_params": safe_json_dumps(response_params_raw),
            "identity_id": identity_id,
            "session_id": session_id,
            "account_id": str(account_id)
          })

          # Process resource table from responseElements.instancesSet (for EC2 instance events)
          response_elements = record.get("responseElements") or {}
          instances_set = response_elements.get("instancesSet", {}) or {}
          items = instances_set.get("items", []) or []
          for item in items:
            natural_name = safe_get(item, "instanceId")
            if natural_name and natural_name not in resources_set:
              resources_set.add(natural_name)
              generated_resource_id = generate_resource_id()
              resource_rows.append({
                "resource_id": generated_resource_id,
                "resource_name": natural_name,
                "resource_type": "ec2instance",
                "additional_metadata": safe_json_dumps(item)
              })
              event_resource_rows.append({
                "event_id": event_id,
                "resource_id": generated_resource_id,
                "pre_state": safe_get(item.get("previousState"), "name"),
                "post_state": safe_get(item.get("currentState"), "name")
              })

          # Process resource table inferred from requestParameters as fallback
          resource_type, extra_metadata = infer_resource_type(record.get("requestParameters") or {})
          if resource_type:
            natural_name = safe_get(record.get("requestParameters") or {}, "name")
            if not natural_name:
              natural_name = safe_get(record.get("requestParameters") or {}, "bucketName")
            if not natural_name:
              natural_name = safe_get(record.get("requestParameters") or {}, "instanceId")
            if natural_name and natural_name not in resources_set:
              resources_set.add(natural_name)
              generated_resource_id = generate_resource_id()
              resource_rows.append({
                "resource_id": generated_resource_id,
                "resource_name": natural_name,
                "resource_type": resource_type,
                "additional_metadata": safe_json_dumps(extra_metadata)
              })
              event_resource_rows.append({
                "event_id": event_id,
                "resource_id": generated_resource_id,
                "pre_state": "",
                "post_state": ""
              })
    except Exception as e:
      print(f"Error processing file {file_path}: {e}")

  # Return data lists for each table
  return accounts_rows, identity_rows, session_rows, event_rows, resource_rows, event_resource_rows


def create_tables(spark, database):
  """
  Create namespace and 6 tables (account, identity, session, event, resource, eventresource)
  in the specified database using the default warehouse from the REST catalog.
  All names are in lowercase.
  """
  # Create namespace
  spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {database}")
  print(f"Namespace '{database}' created or already exists.")

  # Create account table
  spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {database}.account (
            account_id STRING,
            account_alias STRING,
            email STRING,
            phone STRING
        )
        USING iceberg
    """)
  print("account table created.")

  # Create identity table
  spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {database}.identity (
            identity_id STRING,
            type STRING,
            principal_id STRING,
            arn STRING,
            user_name STRING,
            account_id STRING
        )
        USING iceberg
    """)
  print("identity table created.")

  # Create session table
  spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {database}.session (
            session_id STRING,
            creation_date TIMESTAMP,
            mfa_authenticated BOOLEAN,
            additional_info STRING,
            identity_id STRING
        )
        USING iceberg
    """)
  print("session table created.")

  # Create event table
  spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {database}.event (
            event_id STRING,
            event_time TIMESTAMP,
            event_source STRING,
            event_name STRING,
            source_ip STRING,
            user_agent STRING,
            request_params STRING,
            response_params STRING,
            identity_id STRING,
            session_id STRING,
            account_id STRING
        )
        USING iceberg
    """)
  print("event table created.")

  # Create resource table
  spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {database}.resource (
            resource_id STRING,
            resource_name STRING,
            resource_type STRING,
            additional_metadata STRING
        )
        USING iceberg
    """)
  print("resource table created.")

  # Create eventresource table
  spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {database}.eventresource (
            event_id STRING,
            resource_id STRING,
            pre_state STRING,
            post_state STRING
        )
        USING iceberg
    """)
  print("eventresource table created.")


def insert_data_in_batches(spark, data, table_name, database, columns, batch_size=100000, insert_sql_template=None):
  """
  Insert data into a table in batches using Spark SQL.
  :param spark: SparkSession
  :param data: List of dicts representing rows.
  :param table_name: Target table name (in lowercase)
  :param database: Target namespace (database)
  :param columns: List of column names in the desired order.
  :param batch_size: Maximum number of rows per batch.
  :param insert_sql_template: Optional customized SQL template (with placeholders {database}, {table}, {view})
  """
  total = len(data)
  print(f"Inserting {total} rows into {database}.{table_name} in batches of {batch_size}...")
  for start in range(0, total, batch_size):
    chunk = data[start:start + batch_size]
    df_chunk = spark.createDataFrame(chunk)
    # Ensure correct column order by selecting the columns explicitly
    df_chunk = df_chunk.select(*columns)
    view_name = f"temp_{table_name}"
    df_chunk.createOrReplaceTempView(view_name)
    if insert_sql_template:
      sql_str = insert_sql_template.format(database=database, table=table_name, view=view_name)
    else:
      sql_str = f"INSERT INTO {database}.{table_name} SELECT * FROM {view_name}"
    spark.sql(sql_str)
    print(f"Inserted rows {start} to {start + len(chunk)} into {database}.{table_name}.")


def insert_data(spark, accounts, identity, session, event, resource, eventresource, database):
  """
  Insert data for each table in batches, specifying column order to avoid schema misalignment.
  """
  # Insert account table: columns order: account_id, account_alias, email, phone
  if accounts:
    insert_data_in_batches(spark, accounts, "account", database,
                           columns=["account_id", "account_alias", "email", "phone"])
  # Insert identity table: columns order: identity_id, type, principal_id, arn, user_name, account_id
  if identity:
    insert_data_in_batches(spark, identity, "identity", database,
                           columns=["identity_id", "type", "principal_id", "arn", "user_name", "account_id"])
  # Insert session table: columns order: session_id, creation_date, mfa_authenticated, additional_info, identity_id
  if session:
    insert_sql = ("""
            INSERT INTO {database}.session 
            SELECT session_id, CAST(creation_date AS TIMESTAMP) AS creation_date, 
                   mfa_authenticated, additional_info, identity_id 
            FROM {view}
        """)
    insert_data_in_batches(spark, session, "session", database,
                           columns=["session_id", "creation_date", "mfa_authenticated", "additional_info",
                                    "identity_id"],
                           insert_sql_template=insert_sql)
  # Insert event table: columns order: event_id, event_time, event_source, event_name, source_ip, user_agent,
  # request_params, response_params, identity_id, session_id, account_id
  if event:
    insert_sql = ("""
            INSERT INTO {database}.event 
            SELECT event_id, CAST(event_time AS TIMESTAMP) AS event_time, event_source, event_name, 
                   source_ip, user_agent, request_params, response_params, identity_id, session_id, 
                   CAST(account_id AS STRING) as account_id
            FROM {view}
        """)
    insert_data_in_batches(spark, event, "event", database,
                           columns=["event_id", "event_time", "event_source", "event_name", "source_ip", "user_agent",
                                    "request_params", "response_params", "identity_id", "session_id", "account_id"],
                           insert_sql_template=insert_sql)
  # Insert resource table: columns order: resource_id, resource_name, resource_type, additional_metadata
  if resource:
    insert_data_in_batches(spark, resource, "resource", database,
                           columns=["resource_id", "resource_name", "resource_type", "additional_metadata"])
  # Insert eventresource table: columns order: event_id, resource_id, pre_state, post_state
  if eventresource:
    insert_data_in_batches(spark, eventresource, "eventresource", database,
                           columns=["event_id", "resource_id", "pre_state", "post_state"])


def main():
  parser = argparse.ArgumentParser(
    description="Convert JSON file(s) to Parquet and insert data into S3 Tables using Spark SQL."
  )
  parser.add_argument("json_folder", help="Path to the folder containing JSON files.")
  parser.add_argument("--database", default="security_graph",
                      help="Target database (namespace) in the REST catalog. Use lowercase.")
  args = parser.parse_args()

  # Create SparkSession; external spark-submit should pass necessary catalog configs
  spark = SparkSession.builder.appName("JsonToS3Tables").getOrCreate()

  # Create namespace and tables
  create_tables(spark, args.database)

  # Process JSON files and obtain data for each table
  accounts, identity, session, event, resource, eventresource = process_files(args.json_folder)

  # Insert data into tables via Spark SQL
  insert_data(spark, accounts, identity, session, event, resource, eventresource, args.database)

  print("Data processing and insertion completed.")

  spark.stop()


if __name__ == "__main__":
  main()
