#!/usr/bin/env python3
import argparse
import json
import os
import uuid

import ijson
import pandas as pd
from faker import Faker

# Initialize Faker for generating sample account details
fake = Faker()


def generate_session_id(identity_id, creation_date):
  """Generate a simple session_id by concatenating identity_id and creation_date."""
  return f"{identity_id}_{creation_date}"


def generate_resource_id():
  """Generate a random UUID as resource_id."""
  return str(uuid.uuid4())


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


def process_files(input_folder, output_folder):
  """
    Process all JSON files in the input folder (each should have a top-level "Records" array),
    extract data for Account, Identity, Session, Event, Resource, and EventResource tables,
    and then write each table to a Parquet file in the output folder.

    The output files are: Account.parquet, Identity.parquet, Session.parquet,
    Event.parquet, Resource.parquet, EventResource.parquet.
    """
  # Create output folder if it doesn't exist
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)

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

  # Process each JSON file in the input folder (files with .json extension)
  json_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.json')]
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
                "creation_date": creation_date,
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
    except Exception as e:
      print(f"Error processing file {file_path}: {e}")

  # After processing all files, convert lists to DataFrames and write to Parquet files
  def write_parquet(data_rows, out_file):
    try:
      df = pd.DataFrame(data_rows)
      df.to_parquet(out_file, engine='pyarrow', index=False)
      print(f"Wrote {len(data_rows)} rows to {out_file}")
    except Exception as e:
      print(f"Error writing {out_file}: {e}")

  # Define output file paths for each table
  out_account = os.path.join(output_folder, "Account.parquet")
  out_identity = os.path.join(output_folder, "Identity.parquet")
  out_session = os.path.join(output_folder, "Session.parquet")
  out_event = os.path.join(output_folder, "Event.parquet")
  out_resource = os.path.join(output_folder, "Resource.parquet")
  out_event_resource = os.path.join(output_folder, "EventResource.parquet")

  write_parquet(accounts_rows, out_account)
  write_parquet(identity_rows, out_identity)
  write_parquet(session_rows, out_session)
  write_parquet(event_rows, out_event)
  write_parquet(resource_rows, out_resource)
  write_parquet(event_resource_rows, out_event_resource)

  print("Parquet files have been generated in folder:", output_folder)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Convert JSON file(s) with a top-level 'Records' array directly into Parquet files for Account, Identity, Session, Event, Resource, and EventResource tables."
  )
  parser.add_argument("json_file_or_folder", help="Path to the JSON file or folder containing JSON files.")
  parser.add_argument("output_folder", help="Folder to save the output Parquet files.")
  args = parser.parse_args()

  # Default input is a file or folder; output folder will be created if necessary.
  input_path = args.json_file_or_folder
  output_folder = args.output_folder
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)

  if os.path.isfile(input_path):
    process_files(os.path.dirname(input_path), output_folder)
  elif os.path.isdir(input_path):
    process_files(input_path, output_folder)
  else:
    print(f"The path {input_path} is neither a file nor a directory.")
