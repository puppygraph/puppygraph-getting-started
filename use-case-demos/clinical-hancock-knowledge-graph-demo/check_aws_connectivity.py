"""Read-only AWS connectivity smoke test for the demo pipeline."""

import argparse
import os
import sys

import boto3
from pyiceberg.catalog import load_catalog

from config import GLUE_DATABASE, GLUE_WAREHOUSE, S3_BUCKET, S3_PREFIX


def parse_args():
    parser = argparse.ArgumentParser(description="Run read-only AWS connectivity checks")
    parser.add_argument("--profile", help="Optional AWS profile to use for this test")
    return parser.parse_args()


def check_sts_identity():
    identity = boto3.client("sts").get_caller_identity()
    print(f"[OK] STS identity: {identity['Arn']}")


def check_s3_access():
    s3 = boto3.client("s3")
    s3.head_bucket(Bucket=S3_BUCKET)
    result = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=f"{S3_PREFIX}/", MaxKeys=3)
    print(f"[OK] S3 access: visible keys under prefix sample={result.get('KeyCount', 0)}")


def check_glue_database():
    glue = boto3.client("glue")
    try:
        glue.get_database(Name=GLUE_DATABASE)
        print(f"[OK] Glue database reachable: {GLUE_DATABASE}")
    except glue.exceptions.EntityNotFoundException:
        # For a read-only connectivity test, a missing database should not be fatal.
        # The fact that we received this exception means Glue is reachable and
        # our caller is authorized to make the request.
        print(f"[WARN] Glue reachable but database not found: {GLUE_DATABASE}")


def check_pyiceberg_catalog():
    catalog = load_catalog("glue", **{"type": "glue", "warehouse": GLUE_WAREHOUSE})
    namespaces = catalog.list_namespaces()
    print(f"[OK] PyIceberg catalog reachable: namespace_count={len(namespaces)}")


def main():
    args = parse_args()

    if args.profile:
        os.environ["AWS_PROFILE"] = args.profile

    print("=== Read-only connectivity smoke test ===")
    print(f"S3 bucket: {S3_BUCKET}")
    print(f"S3 prefix: {S3_PREFIX}")
    print(f"Glue database: {GLUE_DATABASE}")
    print(f"Glue warehouse: {GLUE_WAREHOUSE}")

    checks = [
        ("STS identity", check_sts_identity),
        ("S3 access", check_s3_access),
        ("Glue database", check_glue_database),
        ("PyIceberg catalog", check_pyiceberg_catalog),
    ]

    failures = []
    for label, check in checks:
        try:
            check()
        except Exception as exc:
            failures.append((label, exc))
            print(f"[FAIL] {label}: {exc}")

    if failures:
        print("RESULT: FAIL")
        sys.exit(1)

    print("RESULT: PASS")


if __name__ == "__main__":
    main()
