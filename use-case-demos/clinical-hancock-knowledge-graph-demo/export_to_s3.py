"""Export parquet data to AWS S3 General Bucket"""

from pathlib import Path
from tempfile import TemporaryDirectory
import boto3
import duckdb
from config import DB_PATH, TABLES, S3_BUCKET, S3_PREFIX

def main():
    s3 = boto3.client("s3")
    conn = duckdb.connect(DB_PATH)

    try:
        with TemporaryDirectory() as tmp_dir:
            for table in TABLES:
                filename = f"{S3_PREFIX}/{table}/{table}_part0.parquet"
                out_path = Path(tmp_dir) / f"{table}_part0.parquet"

                try:
                    conn.execute(f"COPY (SELECT * FROM {table}) TO '{out_path}' (FORMAT PARQUET)")
                    s3.upload_file(str(out_path), S3_BUCKET, filename)
                except Exception as exc:
                    target = f"s3://{S3_BUCKET}/{filename}"
                    raise RuntimeError(f"Failed exporting {table} to {target}") from exc

    finally:
        conn.close()

if __name__ == "__main__":
    main()
