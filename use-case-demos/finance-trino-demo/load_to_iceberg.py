import glob
import os

import yaml
import pyarrow.parquet as pq
from pyiceberg.catalog.rest import RestCatalog
from pyiceberg.exceptions import NamespaceAlreadyExistsError

# ── Load config ───────────────────────────────────────────────────────
_cfg_path = os.path.join(os.path.dirname(__file__), "config.yml")
with open(_cfg_path) as f:
    cfg = yaml.safe_load(f)

s3 = cfg["s3"]
NAMESPACE    = cfg["namespace"]
PARQUET_BASE = os.path.join(os.path.dirname(__file__), cfg["parquet_base"])

# Discover tables from subdirectory names under parquet_data/
TABLES = sorted(
    name for name in os.listdir(PARQUET_BASE)
    if os.path.isdir(os.path.join(PARQUET_BASE, name))
)

# ── Init catalog ──────────────────────────────────────────────────────
catalog = RestCatalog(
    name="default",
    **{
        "uri": cfg["catalog_uri"],
        "s3.endpoint": s3["endpoint"],
        "s3.access-key-id": s3["access_key"],
        "s3.secret-access-key": s3["secret_key"],
        "s3.region": s3["region"],
        "s3.path-style-access": str(s3["path_style_access"]).lower(),
    },
)

# ── Create namespace ──────────────────────────────────────────────────
try:
    catalog.create_namespace(NAMESPACE)
    print(f"Namespace '{NAMESPACE}' created.")
except NamespaceAlreadyExistsError:
    print(f"Namespace '{NAMESPACE}' already exists, skipping.")

# ── Load each table ───────────────────────────────────────────────────
for table_name in TABLES:
    table_dir = os.path.join(PARQUET_BASE, table_name)
    if not glob.glob(os.path.join(table_dir, "*.parquet")):
        print(f"[WARN] No parquet files found: {table_name}, skipping.")
        continue

    arrow_table = pq.read_table(table_dir)
    full_name = f"{NAMESPACE}.{table_name}"

    # Drop existing table for idempotency
    try:
        catalog.drop_table(full_name)
        print(f"  Dropped existing: {full_name}")
    except Exception:
        pass

    iceberg_table = catalog.create_table(full_name, schema=arrow_table.schema)
    iceberg_table.append(arrow_table)
    print(f"[OK] {full_name}: {len(arrow_table)} rows")

print("\nDone.")
