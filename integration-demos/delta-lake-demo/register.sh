#!/usr/bin/env bash
UC_SERVER="${UC_SERVER:-http://localhost:9000}"
CATALOG="${CATALOG:-puppygraph}"
SCHEMA="${SCHEMA:-modern}"
DELTA_BASE="${DELTA_BASE:-file:///delta/demo}"

json_header=(-H "Content-Type: application/json")

# Create puppygraph catalog
curl -sS -X POST "${UC_SERVER}/api/2.1/unity-catalog/catalogs" "${json_header[@]}" \
  -d "{\"name\":\"${CATALOG}\"}"

# Create modern schema
curl -sS -X POST "${UC_SERVER}/api/2.1/unity-catalog/schemas" "${json_header[@]}" \
  -d "{\"name\":\"${SCHEMA}\",\"catalog_name\":\"${CATALOG}\"}"

# Register 4 tables: person, knows, software, created
for t in person knows software created; do
  curl -sS -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" "${json_header[@]}" \
    -d "{\"name\":\"${t}\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/${t}\"}"
done