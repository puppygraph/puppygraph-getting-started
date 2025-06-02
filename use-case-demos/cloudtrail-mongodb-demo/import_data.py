#!/usr/bin/env python3
import argparse
import json
import os
import uuid

import ijson
import pandas as pd
from faker import Faker
from pymongo import MongoClient

CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")

# Initialize Faker for generating sample account details
fake = Faker()

COLLECTION_SCHEMA = {
  "Account": {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["account_id", "account_alias", "email"],
        "properties": {
            "account_id": { "bsonType": "string" },
            "account_alias": { "bsonType": "string" },
            "email": { "bsonType": "string" },
            "phone": { "bsonType": "string" }
        }
    }
  },
  "Event": {
    "$jsonSchema": {
      "bsonType": "object",
      "required": ["event_id", "event_time", "event_source", "event_name", "identity_id", "account_id"],
      "properties": {
        "event_id": { "bsonType": "string" },
        "event_time": { "bsonType": "date" },
        "event_source": { "bsonType": "string" },
        "event_name": { "bsonType": "string" },
        "source_ip": { "bsonType": "string" },
        "user_agent": { "bsonType": "string" },
        "request_params": { "bsonType": "string" },
        "response_params": { "bsonType": "string" },
        "identity_id": { "bsonType": "string" },
        "session_id": { "bsonType": "string" },
        "account_id": { "bsonType": "string" }
      }
    }
  },
  "EventResource": {
    "$jsonSchema": {
      "bsonType": "object",
      "required": ["event_id", "resource_id"],
      "properties": {
        "event_id": { "bsonType": "string" },
        "resource_id": { "bsonType": "string" },
        "pre_state": { "bsonType": "string" },
        "post_state": { "bsonType": "string" }
      }
    }
  },
  "Identity": {
    "$jsonSchema": {
      "bsonType": "object",
      "required": ["identity_id", "type", "principal_id", "arn", "user_name", "account_id"],
      "properties": {
        "identity_id": { "bsonType": "string" },
        "type": { "bsonType": "string" },
        "principal_id": { "bsonType": "string" },
        "arn": { "bsonType": "string" },
        "user_name": { "bsonType": "string" },
        "account_id": { "bsonType": "string" }
      }
    }
  },
  "Resource":{
    "$jsonSchema": {
      "bsonType": "object",
      "required": ["resource_id", "resource_name", "resource_type"],
      "properties": {
        "resource_id": { "bsonType": "string" },
        "resource_name": { "bsonType": "string" },
        "resource_type": { "bsonType": "string" },
        "additional_metadata": { "bsonType": "string" }
      }
    }
  },
  "Session": {
    "$jsonSchema": {
      "bsonType": "object",
      "required": ["session_id", "creation_date", "mfa_authenticated", "identity_id"],
      "properties": {
        "session_id": { "bsonType": "string" },
        "creation_date": { "bsonType": "date" },
        "mfa_authenticated": { "bsonType": "bool" },
        "additional_info": { "bsonType": "string" },
        "identity_id": { "bsonType": "string" }
      }
    }
  }
}


def batch_insert(collection, documents, batch_size=10000):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        try:
            collection.insert_many(batch)
            print(f"Inserted batch {i//batch_size + 1}")
        except Exception as e:
            print(f"Error in batch {i//batch_size + 1}: {e}")


def generate_session_id(identity_id, creation_date):
  """Generate a simple session_id by concatenating identity_id and creation_date."""
  return f"{identity_id}_{creation_date}"


def generate_resource_id():
  """Generate a random UUID as resource_id."""
  return str(uuid.uuid4())


def safe_time_strptime(date_str, date_format="%Y-%m-%dT%H:%M:%SZ"):
  """
    Safely parse a date string into a datetime object.
    Returns None if the string is empty or None.
    """
  if date_str:
    try:
      return pd.to_datetime(date_str, format=date_format)
    except ValueError:
      print(f"Error parsing date: {date_str}")
  return None


def safe_json_dumps(data):
  """
    Convert data to JSON string.
    Use default=str to convert non-serializable types (like Decimal) to string.
    Return an empty string if data is None.
    """
  return json.dumps(data, ensure_ascii=False, default=str) if data is not None else ""


def safe_get(data, key, default=''):
  """
    Safely get a value from a dictionary.
    Returns default if key is missing or value is None.
    """
  if data is None:
    return default
  return data.get(key) or default


def infer_resource_type(request_params):
  """
    Infer a resource type string based on keys in requestParameters.
    Returns a tuple: (resource_type, extra_metadata).
    """
  if not request_params:
    return '', {}

  # CloudTrail Trail
  if 'trailNameList' in request_params or ('name' in request_params and (
          's3BucketName' in request_params or 'enableLogFileValidation' in request_params)):
    return 'CloudTrailTrail', {}

  # S3 Bucket related requests
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
    return 'S3Bucket', {}

  # EC2 Instance related
  if 'instancesSet' in request_params:
    return 'EC2Instance', {}

  # AMI / Images
  if 'imagesSet' in request_params or (
          'imageId' in request_params and request_params.get('imageId', '').startswith('ami-')):
    return 'AMI', {}

  # Volume related
  if 'volumeSet' in request_params or 'volumeId' in request_params:
    return 'Volume', {}

  # Snapshot related
  if 'snapshotSet' in request_params or 'snapshotId' in request_params:
    return 'Snapshot', {}

  # Availability Zone
  if 'availabilityZoneSet' in request_params:
    return 'AvailabilityZone', {}

  # Security Group
  if 'securityGroupSet' in request_params or 'securityGroupIdSet' in request_params or 'ipPermissions' in request_params:
    return 'SecurityGroup', {}

  # Subnet
  if 'subnetSet' in request_params or 'subnetId' in request_params:
    return 'Subnet', {}

  # VPC
  if 'vpcSet' in request_params or 'vpcId' in request_params:
    return 'VPC', {}

  # IAM Role related
  if 'roleName' in request_params and (
          'assumeRolePolicyDocument' in request_params or 'policyDocument' in request_params):
    return 'IAMRole', {}

  # IAM Policy related
  if 'policyName' in request_params or 'policyArn' in request_params:
    return 'IAMPolicy', {}

  # Instance Profile
  if 'instanceProfileName' in request_params:
    return 'IAMInstanceProfile', {}

  # Lambda Function
  if 'functionName' in request_params and 'handler' in request_params:
    return 'LambdaFunction', {}

  # API Gateway related (could be refined further)
  if 'restApiId' in request_params:
    return 'APIGateway', {}

  # CloudFormation Stack
  if 'stackStatusFilter' in request_params:
    return 'CloudFormationStack', {}

  # AWS Config / configuration recorder
  if 'configurationRecorder' in request_params or 'deliveryChannel' in request_params:
    return 'AWSConfig', {}

  # Network related resources
  if 'customerGatewaySet' in request_params:
    return 'CustomerGateway', {}
  if 'dhcpOptionsSet' in request_params:
    return 'DHCPOptions', {}
  if 'networkAclIdSet' in request_params:
    return 'NetworkAcl', {}

  # Reserved Instances or Spot Instance Requests
  if 'reservedInstancesSet' in request_params or 'spotInstanceRequestIdSet' in request_params:
    return 'ReservedOrSpotInstances', {}

  # CodeCommit repository
  if 'repositoryNames' in request_params:
    return 'CodeCommit', {}

  # ACM Certificate
  if 'certificateStatuses' in request_params:
    return 'ACMCertificate', {}

  # MFA Device
  if 'virtualMFADeviceName' in request_params or 'serialNumber' in request_params:
    return 'MFADevice', {}

  # Generic query: keys like maxResults, filterSet, nextToken, pageSize or limit exist
  if any(k in request_params for k in ['maxResults', 'nextToken', 'filterSet', 'pageSize', 'limit']):
    return 'GenericQuery', {}

  # Default: return an empty type
  return '', {}


def process_files(input_path, dbname):
  """
    Process all JSON files in the input folder (each should have a top-level "Records" array),
    extract data for Account, Identity, Session, Event, Resource, and EventResource tables,
    and then write each table to a database in MongoDB Atlas.
    """
  try:
    client = MongoClient(CONNECTION_STRING)
    db = client[dbname]
    for collection_name, schema in COLLECTION_SCHEMA.items():
      if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
      db.create_collection(collection_name, validator=schema)
  except Exception as e:
    print(f"Error connecting to MongoDB and creating collections: {e}")
    return

  # Lists to accumulate rows for each table
  accounts_rows = []
  identity_rows = []
  session_rows = []
  event_rows = []
  resource_rows = []
  event_resource_rows = []

  # Deduplication sets based on natural keys
  accounts_set = set()
  identities_set = set()
  sessions_set = set()
  resources_set = set()  # use natural resource name as key

  if os.path.isfile(input_path):
    input_folder = os.path.dirname(input_path)
    json_files = [os.path.basename(input_path)]
  elif os.path.isdir(input_path):
    # Process each JSON file in the input folder (files with .json extension)
    input_folder = input_path
    json_files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith('.json')])
  
  total_files = len(json_files)
  print(f"Found {total_files} JSON file(s) in {input_folder}.")

  for json_file in json_files:
    file_path = os.path.join(input_folder, json_file)
    print(f"Processing file: {file_path}")
    try:
      with open(file_path, 'r', encoding='utf-8') as f:
        for record in ijson.items(f, "Records.item"):
          # Process Account table
          user_identity = record.get("userIdentity") or {}
          account_id = safe_get(user_identity, "accountId")
          if account_id and account_id not in accounts_set:
            accounts_set.add(account_id)
            accounts_rows.append({
              "account_id": str(account_id),  # Ensure account_id is stored as string
              "account_alias": fake.user_name(),
              "email": fake.email(),
              "phone": fake.phone_number()
            })

          # Process Identity table
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

          # Process Session table
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
                "creation_date": safe_time_strptime(creation_date),
                "mfa_authenticated": str(safe_get(attributes, "mfaAuthenticated", "false")).lower() == "true",
                "additional_info": safe_json_dumps(additional_info),
                "identity_id": identity_id
              })
          else:
            session_id = ""

          # Process Event table
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
            "event_time": safe_time_strptime(event_time),
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

          # Process Resource from responseElements.instancesSet (for EC2 instance events)
          response_elements = record.get("responseElements") or {}
          instances_set = response_elements.get("instancesSet", {}) or {}
          items = instances_set.get("items", []) or []
          for item in items:
            # Prefer resource info from response; assume instanceId is provided as natural name
            natural_name = safe_get(item, "instanceId")
            if natural_name and natural_name not in resources_set:
              resources_set.add(natural_name)
              generated_resource_id = generate_resource_id()
              resource_rows.append({
                "resource_id": generated_resource_id,
                "resource_name": natural_name,
                "resource_type": "EC2Instance",
                "additional_metadata": safe_json_dumps(item)
              })
              event_resource_rows.append({
                "event_id": event_id,
                "resource_id": generated_resource_id,
                "pre_state": safe_get(item.get("previousState"), "name"),
                "post_state": safe_get(item.get("currentState"), "name")
              })

          # Process Resource inferred from requestParameters as fallback
          resource_type, extra_metadata = infer_resource_type(request_params_raw)
          if resource_type:
            # Determine natural name using common keys ("name", "bucketName", "instanceId")
            natural_name = safe_get(request_params_raw, "name")
            if not natural_name:
              natural_name = safe_get(request_params_raw, "bucketName")
            if not natural_name:
              natural_name = safe_get(request_params_raw, "instanceId")
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
      print(f"Processed {len(accounts_rows)} Account rows, {len(identity_rows)} Identity rows, {len(session_rows)} Session rows, {len(event_rows)} Event rows, {len(resource_rows)} Resource rows, and {len(event_resource_rows)} EventResource rows from file: {file_path}")
    except Exception as e:
      print(f"Error processing file {file_path}: {e}")
      return
    
    try:
      # Insert data into MongoDB collections
      print(f"Inserting data into MongoDB collections...")
      if accounts_rows:
        batch_insert(db.Account, accounts_rows)
        print(f"Inserted {len(accounts_rows)} Account rows.")
        accounts_rows = []
      if identity_rows:
        batch_insert(db.Identity, identity_rows)
        print(f"Inserted {len(identity_rows)} Identity rows.")
        identity_rows = []     
      if session_rows:
        batch_insert(db.Session, session_rows)
        print(f"Inserted {len(session_rows)} Session rows.")
        session_rows = []     
      if event_rows:
        batch_insert(db.Event, event_rows)
        print(f"Inserted {len(event_rows)} Event rows.")
        event_rows = []    
      if resource_rows:
        db.Resource.insert_many(resource_rows)
        print(f"Inserted {len(resource_rows)} Resource rows.")
        resource_rows = []   
      if event_resource_rows:
        batch_insert(db.EventResource, event_resource_rows)
        print(f"Inserted {len(event_resource_rows)} EventResource rows.")
        event_resource_rows = []    
    except Exception as e:
      print(f"Error inserting data into MongoDB: {e}")
      return


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Convert data in JSON file(s) with a top-level 'Records' array to MongoDB Atalas for Account, Identity, Session, Event, Resource, and EventResource collections with schema validators."
  )
  parser.add_argument("json_file_or_folder", help="Path to the JSON file or folder containing JSON files.")
  parser.add_argument("--database", default="cloudtrail", help="Target database. Use lowercase.")
  args = parser.parse_args()

  # Default input is a file or folder; output folder will be created if necessary.
  input_path = args.json_file_or_folder

  if os.path.isfile(input_path) or os.path.isdir(input_path):
    process_files(input_path, args.database)
  else:
    print(f"The path {input_path} is neither a file nor a directory.")
