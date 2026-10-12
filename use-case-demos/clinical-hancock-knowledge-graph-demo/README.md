# Clinical Oncology Knowledge Graph Demo

This is a clinical oncology knowledge graph connecting cancer patients to their full diagnostic, pathological, treatment, and outcome histories. Graph use cases include identifying which treatment pathways lead to better survival outcomes, find patients with similar clinical journeys for cohort analysis, and trace how cancer spreads across anatomical sites over time.

Data derived from the [Hancock dataset](https://hancock.research.fau.eu/download).

**Reference:**
Dörrich, M., Balk, M., Heusinger, T. *et al*. A multimodal dataset for precision oncology in head and neck cancer. *Nat Commun* **16**, 7163 (2025). https://doi.org/10.1038/s41467-025-62386-6

---

## Stack

- **DuckDB** — local processing of raw JSON into structured tables and views
- **Apache Iceberg** — tables on a local object store, served through an Iceberg REST catalog
- **Apache Spark** — loads the exported parquet into the Iceberg tables
- **PuppyGraph** — graph layer mapped over the Iceberg tables

Everything runs locally with Docker Compose; no cloud account is needed.

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Data Preparation

### Load JSON into DuckDB

Loads the 4 raw JSON files into DuckDB and creates derived views.

```bash
python build_db.py
```

### Convert DuckDB tables into Parquet

Exports each table and view to `parquet_data/{table}.parquet`.

```bash
python export_parquet.py
```

### Start the stack

Starts the object store, the Iceberg REST catalog, Spark and PuppyGraph:

```bash
docker compose up -d
```

### Load the parquet into Iceberg tables

Creates the `hancock_db` namespace and one Iceberg table per parquet file:

```bash
docker exec spark-iceberg spark-sql -f /sql/load.sql
```

## Connecting to PuppyGraph
### Log into the UI
Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
    - Username: `puppygraph`
    - Password: `puppygraph123`

### Modeling the Graph
Upload the schema:
- Click **Upload Schema**, select the file `schema.json` and click **Upload**.

## Querying via PuppyGraph

Navigate to **Query** in the Web UI:

- Use **Graph Query** for Gremlin/openCypher queries with visualization.

### Example Queries
Refer to [QUERIES.md](docs/QUERIES.md) for a list of example Cypher queries.

### Teardown
- Stop and remove the containers.
  ```bash
  docker compose down
  ```

---

## Design Decisions

**`closest_resection_margin_in_cm`**
Raw values include left-censored entries like `<0.1`. The statistically correct approach for ~25% censoring is multiple imputation using MLE (see [PMC6182903](https://pmc.ncbi.nlm.nih.gov/articles/PMC6182903/)). For demo purposes the `<` prefix is stripped and the upper bound (0.1) is used as the value. The column is then cast from `VARCHAR` to `DOUBLE`.

**Views as first-class tables**
DuckDB views are materialised to parquet and loaded as full Iceberg tables. This keeps the Iceberg schema flat and avoids pushing view logic into PuppyGraph.

**`first_metastases` and `first_progressions`**
These are join tables used exclusively as edge sources in PuppyGraph for `HAD_METASTASIS` and `HAD_PROGRESSION`. They contain only the two FKs needed to link a patient to their first event node.

---

## Schema

See [SCHEMA.md](docs/SCHEMA.md) for full table and column definitions, node/edge counts, and PuppyGraph mappings.