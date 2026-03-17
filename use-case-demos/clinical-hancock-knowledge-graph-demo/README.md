# Clinical Oncology Knowledge Graph Demo

This is a clinical oncology knowledge graph connecting cancer patients to their full diagnostic, pathological, treatment, and outcome histories. Graph use cases include identifying which treatment pathways lead to better survival outcomes, find patients with similar clinical journeys for cohort analysis, and trace how cancer spreads across anatomical sites over time.

Data derived from the [Hancock dataset](https://hancock.research.fau.eu/download).

**Reference:**
Dörrich, M., Balk, M., Heusinger, T. *et al*. A multimodal dataset for precision oncology in head and neck cancer. *Nat Commun* **16**, 7163 (2025). https://doi.org/10.1038/s41467-025-62386-6

---

## Stack

- **DuckDB** — local processing of raw JSON into structured tables and views
- **PyIceberg** — writes parquet data to S3 as Iceberg tables registered in Glue
- **AWS Glue** — catalog layer queried by PuppyGraph
- **PuppyGraph** — graph layer mapped over the Glue tables

---

## Setup

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Configure your AWS profile:

```bash
aws configure --profile hancock-demo
export AWS_PROFILE=hancock-demo
```

Configure your S3 and Glue settings (or leave defaults to use the demo bucket):
```bash
export S3_BUCKET=puppy-aws-hcls-hancock-demo
export S3_PREFIX=parquet_data
export GLUE_DATABASE=hancock_db
export OVERWRITE_GLUE_TABLES=true
```

Run a read-only connectivity smoke test (no data writes):
```bash
python check_aws_connectivity.py --profile hancock-demo
```

---

## Data Preparation

### Load JSON into DuckDB

Loads the 4 raw JSON files into DuckDB and creates derived views.

```bash
python build_db.py
```

### Convert DuckDB tables into Parquet

Exports each table and view as parquet to:

```
s3://{S3_BUCKET}/{S3_PREFIX}/{table}/{table}_part0.parquet
```

Parquet files are generated in a temporary local directory during export and removed automatically after upload.

```bash
python export_to_s3.py
```

### Register Iceberg Tables under Glue Catalog

Reads each parquet file, infers schema from parquet, and creates an Iceberg table in Glue.

This step is a full refresh for demo repeatability: each target table is dropped and recreated before loading data.

Set `OVERWRITE_GLUE_TABLES=false` to keep existing tables and append incoming demo parquet rows instead.

```bash
python write_to_glue.py
```

The Iceberg warehouse (metadata + managed data files) is kept separate from the source parquet:

```
s3://.../parquet_data/   ← source parquet (read from)
s3://.../warehouse/      ← Iceberg warehouse (written to)
```

## Connecting to PuppyGraph
### Start PuppyGraph Instance
Run the command below to start a PuppyGraph Docker container. This command will also download the PuppyGraph image if it hasn't been downloaded previously.
```
docker run -p 8081:8081 -p 8182:8182 -p 7687:7687 \
  -e PUPPYGRAPH_PASSWORD=puppygraph123 \
  -e QUERY_TIMEOUT=5m \
  -e AWS_REGION=<region> \
  -e AWS_ACCESS_KEY_ID=<AccessKeyId> \
  -e AWS_SECRET_ACCESS_KEY=<SecretAccessKey> \
  -d --name puppy --rm --pull=always puppygraph/puppygraph:stable
```

### Log into the UI
Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
    - Username: `puppygraph`
    - Password: `puppygraph123`

### Modeling the Graph
Upload the schema:
- In Web UI, select the file `schema.json` under **Upload Graph Schema JSON**, then click on **Upload**.

Optional: You can also create the schema using the schema builder via click on **Create graph schema**. You will add vertices and edges step by step.

## Querying via PuppyGraph

Navigate to **Query** in the Web UI:

- Use **Graph Query** for Gremlin/openCypher queries with visualization.

### Example Queries

Refer to [QUERIES.md](docs/QUERIES.md) for a list of example Cypher queries.

### Teardown
- Stop the PuppyGraph container.
  ```bash
  docker stop puppy
  ```

---

## Design Decisions

**`closest_resection_margin_in_cm`**
Raw values include left-censored entries like `<0.1`. The statistically correct approach for ~25% censoring is multiple imputation using MLE (see [PMC6182903](https://pmc.ncbi.nlm.nih.gov/articles/PMC6182903/)). For demo purposes the `<` prefix is stripped and the upper bound (0.1) is used as the value. The column is then cast from `VARCHAR` to `DOUBLE`.

**Iceberg field IDs**
DuckDB-exported parquet files do not embed Iceberg field IDs, which PyIceberg requires for schema mapping. Field IDs are assigned sequentially before creating each table.

**Views as first-class tables**
DuckDB views are materialised to parquet and loaded as full Iceberg tables in Glue. This keeps the Glue schema flat and avoids pushing view logic into PuppyGraph.

**`first_metastases` and `first_progressions`**
These are join tables used exclusively as edge sources in PuppyGraph for `HAD_METASTASIS` and `HAD_PROGRESSION`. They contain only the two FKs needed to link a patient to their first event node.

---

## Schema

See [SCHEMA.md](docs/SCHEMA.md) for full table and column definitions, node/edge counts, and PuppyGraph mappings.