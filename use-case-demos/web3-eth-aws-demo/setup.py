import argparse
import os
from pyspark.sql import SparkSession
from config import TABLES, ETH_SCHEMAS, TARGET_BUCKET, TARGET_DB

spark = SparkSession.builder \
    .master("local[*]") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.glue_catalog.type", "glue") \
    .config("spark.sql.catalog.glue_catalog.warehouse", f"s3://{TARGET_BUCKET}/iceberg/") \
    .config("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
    .config("spark.sql.catalog.glue_catalog.client.region", os.environ["AWS_REGION"]) \
    .config("spark.hadoop.fs.s3a.endpoint", f"s3.{os.environ['AWS_REGION']}.amazonaws.com") \
    .config("spark.hadoop.fs.s3.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

def create_table(table_name):
    table_path = f"s3://{TARGET_BUCKET}/iceberg/eth/{table_name}/"

    spark.sql(f"CREATE DATABASE IF NOT EXISTS glue_catalog.{TARGET_DB}")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS glue_catalog.{TARGET_DB}.{table_name} (
            {ETH_SCHEMAS[table_name]}
        )
        USING iceberg
        PARTITIONED BY (date)
        LOCATION '{table_path}'
        TBLPROPERTIES (
            'write.metadata.delete-after-commit.enabled' = 'true',
            'write.metadata.previous-versions-max'       = '10'
        )
    """)
    print(f"{TARGET_DB}.{table_name} created")

def add_files(table_name):
    spark.sql(f"""
        CALL glue_catalog.system.add_files(
            table => 'glue_catalog.{TARGET_DB}.{table_name}',
            source_table => '`parquet`.`s3://{TARGET_BUCKET}/eth/{table_name}/`',
            check_duplicate_files => false
        )
    """)
    print(f"Iceberg metadata created for {table_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--add-files", action="store_true")
    args = parser.parse_args()

    if args.create:
        for table in TABLES:
            create_table(table)

    if args.add_files:
        for table in TABLES:
            try:
                add_files(table)

            except Exception as e:
                if "IllegalStateException" in str(e) and "check_duplicate_files" in str(e):
                    print(f"{table} skipped: partition already loaded")
                else:
                    print(f"{table} failed: {e}")
