import os

from pyspark.sql import SparkSession

catalog_name = "biglake_rest"
namespace = "security_demo"

gcs_bucket = os.environ["GCS_BUCKET"]
gcp_project = os.environ["GCP_PROJECT"]

spark = SparkSession.builder.appName("cloud_security_biglake_drop") \
  .config('spark.jars.packages', 'org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:1.10.1,org.apache.iceberg:iceberg-gcp-bundle:1.10.1') \
  .config(f'spark.sql.catalog.{catalog_name}', 'org.apache.iceberg.spark.SparkCatalog') \
  .config(f'spark.sql.catalog.{catalog_name}.type', 'rest') \
  .config(f'spark.sql.catalog.{catalog_name}.uri', 'https://biglake.googleapis.com/iceberg/v1/restcatalog') \
  .config(f'spark.sql.catalog.{catalog_name}.warehouse', gcs_bucket) \
  .config(f'spark.sql.catalog.{catalog_name}.header.x-goog-user-project', gcp_project) \
  .config(f'spark.sql.catalog.{catalog_name}.rest.auth.type', 'org.apache.iceberg.gcp.auth.GoogleAuthManager') \
  .config(f'spark.sql.catalog.{catalog_name}.io-impl', 'org.apache.iceberg.gcp.gcs.GCSFileIO') \
  .config(f'spark.sql.catalog.{catalog_name}.rest-metrics-reporting-enabled', 'false') \
  .config('spark.sql.extensions', 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions') \
  .config('spark.sql.defaultCatalog', catalog_name) \
  .getOrCreate()

try:
  tables = spark.sql(f"SHOW TABLES IN {namespace}").collect()
  print(f"Found {len(tables)} tables in {namespace}")
except Exception as exc:
  # If the namespace does not exist or cannot be listed, continue cleanup without dropping tables.
  print(f"Could not list tables in namespace {namespace}; skipping table drops. Details: {exc}")
  tables = []

for row in tables:
  print(f"Dropping table {namespace}.{row.tableName}")
  spark.sql(f"DROP TABLE IF EXISTS {namespace}.{row.tableName}")

spark.sql(f"DROP NAMESPACE IF EXISTS {namespace}")
print(f"Dropped namespace {namespace}")

spark.stop()
