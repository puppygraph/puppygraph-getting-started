#!/usr/bin/env bash
UC_SERVER="${UC_SERVER:-http://localhost:9000}"
CATALOG="${CATALOG:-puppygraph}"
SCHEMA="${SCHEMA:-mimic}"
DELTA_BASE="${DELTA_BASE:-file:///delta/mimic}"

json_header=(-H "Content-Type: application/json")

# Create puppygraph catalog
curl -sS -X POST "${UC_SERVER}/api/2.1/unity-catalog/catalogs" "${json_header[@]}" \
  -d "{\"name\":\"${CATALOG}\"}"

# Create mimic schema
curl -sS -X POST "${UC_SERVER}/api/2.1/unity-catalog/schemas" "${json_header[@]}" \
  -d "{\"name\":\"${SCHEMA}\",\"catalog_name\":\"${CATALOG}\"}"

# Register tables

tables=(
  "person"
  "observation_period"
  "visit_occurrence"
  "visit_detail"
  "condition_occurrence"
  "drug_exposure"
  "procedure_occurrence"
  "device_exposure"
  "measurement"
  "observation"
  "death"
  "note"
  "note_nlp"
  "specimen"
  "fact_relationship"
  "location"
  "care_site"
  "provider"
  "payer_plan_period"
  "cost"
  "drug_era"
  "dose_era"
  "condition_era"
  "metadata"
  "cdm_source"
  "concept"
  "vocabulary"
  "concept_relationship"
  "cohort_definition"
  "cohort"
  "cohort_attribute"
  "attribute_definition"
)

for t in "${tables[@]}"; do
  curl -sS -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" "${json_header[@]}" \
    -d "{\"name\":\"${t}\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/${t}\"}"
done