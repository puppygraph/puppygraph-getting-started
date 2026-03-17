"""Constants used for demo"""

import os


def _env_bool(name, default):
    value = os.environ.get(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False

    raise ValueError(f"Invalid boolean value for {name}: {value}")

TABLES = [
    'blood_data_reference_ranges',
    'blood_data',
    'clinical_data',
    'pathological_data',
    'metastases',
    'first_metastases',
    'progressions',
    'first_progressions',
    'recurrences',
    'blood_test_reference_ranges',
    'adjuvant_treatments',
]

DB_PATH = 'hancock_demo.db'
S3_BUCKET = os.environ.get("S3_BUCKET", "puppy-aws-hcls-hancock-demo")
S3_PREFIX = os.environ.get("S3_PREFIX", "parquet_data")
GLUE_DATABASE = os.environ.get("GLUE_DATABASE", "hancock_db")
GLUE_WAREHOUSE = f"s3://{S3_BUCKET}/warehouse/"
OVERWRITE_GLUE_TABLES = _env_bool("OVERWRITE_GLUE_TABLES", True)
