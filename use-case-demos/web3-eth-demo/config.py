import os

TABLES = ["transactions", "token_transfers"]
SOURCE_BUCKET = "aws-public-blockchain"
SOURCE_REGION = "us-east-2"
DATA_DIR = "parquet_data"
DATE_START = os.environ.get("DATE_START", "2026-01-01")
DATE_END = os.environ.get("DATE_END", "2026-01-01")
