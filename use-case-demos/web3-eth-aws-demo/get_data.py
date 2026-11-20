import argparse
from datetime import date, timedelta
from config import DATE_START, DATE_END, TABLES, SOURCE_BUCKET, TARGET_BUCKET
import subprocess
import os

parser = argparse.ArgumentParser()
parser.add_argument("--profile")
args = parser.parse_args()

if args.profile:
    os.environ["AWS_PROFILE"] = args.profile

start = date.fromisoformat(DATE_START)
end = date.fromisoformat(DATE_END)

current = start
while current <= end:
    date_str = current.isoformat()
    prefix = f"date={date_str}/"

    for table in TABLES:
        source = f"s3://{SOURCE_BUCKET}/v1.0/eth/{table}/{prefix}"
        dest = f"s3://{TARGET_BUCKET}/eth/{table}/{prefix}"

        print(f"Syncing {table} for {date_str}...")
        subprocess.run(
            ["aws", "s3", "cp", source, dest, "--recursive"],
            check=True
        )

    current += timedelta(days=1)
