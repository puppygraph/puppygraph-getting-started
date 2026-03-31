import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType

catalog_name = "biglake_rest"
namespace = "security_demo"
csv_dir = os.path.join(os.getcwd(), "csv_data")

gcs_bucket = os.environ["GCS_BUCKET"]
gcp_project = os.environ["GCP_PROJECT"]

spark = SparkSession.builder.appName("cloud_security_biglake_data") \
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

spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {namespace}")
spark.sql(f"USE {namespace}")

# Column casts to ensure correct Iceberg types.
# Spark's CSV reader infers all timestamps as strings and may
# misinterpret nullable ints or numeric-looking strings.
table_casts = {
  "Users": {
    "created_at": "timestamp",
    "last_login": "timestamp",
    "failed_login_attempts": "int",
  },
  "UserInternetGatewayAccess": {
    "granted_at": "timestamp",
    "expires_at": "timestamp",
    "last_accessed_at": "timestamp",
  },
  "UserInternetGatewayAccessLog": {
    "access_time": "timestamp",
  },
  "NetworkInterfaces": {
    "security_group_id": "long",
  },
  "IngressRules": {
    "port_range": "string",
  },
}

# Read each CSV, cast columns, and write as an Iceberg table
for file_name in sorted(os.listdir(csv_dir)):
  if not file_name.endswith(".csv"):
    continue

  table_name = file_name.replace(".csv", "")
  file_path = os.path.join(csv_dir, file_name)

  print(f"Uploading {file_name} -> {catalog_name}.{namespace}.{table_name}")

  df = spark.read.option("header", "true").option("inferSchema", "true").csv(file_path)

  # Cast all int columns to long to match the schema
  for field in df.schema.fields:
    if isinstance(field.dataType, IntegerType):
      df = df.withColumn(field.name, col(field.name).cast("long"))

  # Apply additional column casts if needed
  if table_name in table_casts:
    for column, target_type in table_casts[table_name].items():
      df = df.withColumn(column, col(column).cast(target_type))

  df.writeTo(f"{catalog_name}.{namespace}.{table_name}").createOrReplace()

  print(f"  Done. Row count: {df.count()}")

spark.stop()
print("All tables uploaded successfully.")
