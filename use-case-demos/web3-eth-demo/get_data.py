import sys
from datetime import date, timedelta
from pathlib import Path

import boto3
from botocore import UNSIGNED
from botocore.config import Config

from config import DATA_DIR, DATE_END, DATE_START, SOURCE_BUCKET, SOURCE_REGION, TABLES

s3 = boto3.client("s3", region_name=SOURCE_REGION, config=Config(signature_version=UNSIGNED))
current = date.fromisoformat(DATE_START)
end = date.fromisoformat(DATE_END)
while current <= end:
    for table in TABLES:
        prefix = f"v1.0/eth/{table}/date={current.isoformat()}/"
        print(f"Downloading {prefix}")
        downloaded = 0
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=SOURCE_BUCKET, Prefix=prefix):
            for obj in page.get("Contents", []):
                target = Path(DATA_DIR) / table / f"date={current.isoformat()}" / Path(obj["Key"]).name
                target.parent.mkdir(parents=True, exist_ok=True)
                s3.download_file(SOURCE_BUCKET, obj["Key"], str(target))
                downloaded += 1
        if downloaded == 0:
            sys.exit(f"No objects under s3://{SOURCE_BUCKET}/{prefix}: check the {table} table name and the DATE_START/DATE_END range")
    current += timedelta(days=1)
