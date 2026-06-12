import argparse
import os
import sys
import boto3
from botocore import UNSIGNED
from botocore.config import Config

from config import SOURCE_BUCKET, TARGET_BUCKET, TARGET_DB


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile")
    return parser.parse_args()


def check_sts_identity():
    identity = boto3.client("sts").get_caller_identity()
    print(f"[OK] STS identity: {identity['Arn']}")


def check_source_bucket():
    s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    result = s3.list_objects_v2(
        Bucket=SOURCE_BUCKET,
        Prefix="v1.0/eth/transactions/",
        MaxKeys=3
    )
    print(f"[OK] Source bucket readable: sample={result.get('KeyCount', 0)} keys")


def check_target_bucket():
    s3 = boto3.client("s3")
    s3.head_bucket(Bucket=TARGET_BUCKET)
    print(f"[OK] Target bucket reachable: {TARGET_BUCKET}")


def check_glue_database():
    glue = boto3.client("glue")
    try:
        glue.get_database(Name=TARGET_DB)
        print(f"[OK] Glue database found: {TARGET_DB}")
    except glue.exceptions.EntityNotFoundException:
        # Glue is reachable and we're authorized — database just hasn't been created yet
        print(f"[WARN] Glue reachable but database not found yet: {TARGET_DB}")


def main():
    args = parse_args()

    if args.profile:
        os.environ["AWS_PROFILE"] = args.profile

    print("=== Read-only connectivity smoke test ===")
    print(f"Source bucket : {SOURCE_BUCKET}")
    print(f"Target bucket : {TARGET_BUCKET}")
    print(f"Glue database : {TARGET_DB}")
    print()

    checks = [
        ("STS identity",    check_sts_identity),
        ("Source bucket",   check_source_bucket),
        ("Target bucket",   check_target_bucket),
        ("Glue database",   check_glue_database),
    ]

    failures = []
    for label, check in checks:
        try:
            check()
        except Exception as exc:
            failures.append((label, exc))
            print(f"[FAIL] {label}: {exc}")

    print()
    if failures:
        print("RESULT: FAIL")
        sys.exit(1)

    print("RESULT: PASS")


if __name__ == "__main__":
    main()