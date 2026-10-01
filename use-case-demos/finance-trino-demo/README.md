# SQL and Graph Analytics on Apache Iceberg with Trino and PuppyGraph

## Summary

This demo showcases how to combine **Trino** (SQL OLAP engine) with **PuppyGraph** (graph analytics)
over synthetic financial data in **Apache Iceberg**, inspired by the LDBC Financial Benchmark —
no separate graph database needed, as PuppyGraph queries Iceberg tables directly.

As data preparation, we first load local Parquet files into Iceberg (via MinIO object storage).
Then two complementary analytics patterns run on the same data:

1. **SQL analytics via Trino** — aggregations, joins, and window functions.
2. **Graph analytics via PuppyGraph** — multi-hop path traversal using Cypher.

## Architecture: Dual-Path Data Access

At the storage layer, data resides in Apache Iceberg tables backed by MinIO object storage. Trino provides a distributed SQL query engine that accesses these Iceberg tables through
its connector framework, exposing them via a unified SQL interface.

PuppyGraph can access this data in two ways:

1. **Through Trino (JDBC)** — PuppyGraph [connects to Trino](https://docs.puppygraph.com/connecting/connecting-to-trino) using its JDBC driver and queries the
   same relational tables that are available for SQL analytics. In this demo, all **vertex tables**
   (Account, Company, Loan, Medium, Person) use this path, defined as `trino_catalog` in
   the schema.

2. **Direct connection (Iceberg REST Catalog)** — PuppyGraph [connects directly to the Iceberg REST
   Catalog](https://docs.puppygraph.com/connecting/connecting-to-iceberg/#iceberg-rest) to read table data without going through Trino. In this demo, all **edge tables**
   (e.g., AccountTransferAccount, PersonOwnAccount, LoanDepositAccount) use this path, defined as
   `iceberg_catalog` in the schema.

In both cases, PuppyGraph catalogs define how external systems are accessed and how relational
tables are mapped into graph structures (vertices and edges). This creates a graph view over the
underlying datasets without copying data into a separate graph database.

This architecture allows SQL analytics and graph analytics to operate on the same underlying data.
Analysts can move from large-scale SQL aggregation to relationship exploration without duplicating
data or maintaining separate graph pipelines.

## Project Structure

```
├── README.md                          # This file
├── docker-compose.yml                 # Trino, PuppyGraph, Iceberg REST, MinIO, mc
├── versions.env                       # Docker image versions
├── config.yml                         # Python script config (localhost endpoints)
├── load_to_iceberg.py                 # Loads Parquet data into Iceberg
├── schema-v2.json                     # PuppyGraph graph schema v2 (for PuppyGraph 1.x)
├── schema-v1.json                     # PuppyGraph graph schema v1 (for PuppyGraph 0.x)
├── requirements.txt                   # Python dependencies
├── trino/
│   └── catalog/
│       └── iceberg.properties         # Trino Iceberg connector config
└── parquet_data/                      # 18 tables (Parquet files, ~2.2 MB total)
```

## Prerequisites

- [Docker and Docker Compose](https://docs.docker.com/compose/)
- [uv](https://docs.astral.sh/uv/)

## Start the Services

Docker image versions are configured in `versions.env`. Edit this file to set the Docker image versions before starting.

```bash
docker compose --env-file versions.env up -d
```

The services include:
- **Trino** — SQL query engine (port 8080)
- **PuppyGraph** — graph analytics engine (port 8081)
- **Iceberg REST Catalog** — table metadata service (port 8181)
- **MinIO** — S3-compatible object storage (API port 9000, console port 9001)
- **mc** — MinIO client for initial bucket setup

## Setting Up Python Environment

Create a Python virtual environment and install dependencies.

```bash
uv venv --python 3.11 myenv
source myenv/bin/activate
uv pip install -r requirements.txt
```

## Loading Data into Iceberg

After the containers are up and the MinIO bucket is ready, load the Parquet data into Iceberg.

```bash
python load_to_iceberg.py
```

This script reads all 18 tables from `parquet_data/`, creates corresponding Iceberg tables under the
`demo` namespace, and writes the data to MinIO-backed storage.

## Querying in Trino

Connect to Trino using the CLI.

```bash
docker exec -it trino trino
```

Verify that the tables are loaded.

```sql
SHOW TABLES FROM iceberg.demo;
```

Run a SQL OLAP query to analyze the volume of fund flows across different account types in 2022 —
join the transfer and account tables, filter to transactions within 2022, then group by account type
to compute the number of active accounts, transaction count, and total/average/max transfer amounts:

```sql
SELECT
    a.accountType,
    COUNT(DISTINCT t.fromId)               AS active_accounts,
    COUNT(*)                               AS tx_count,
    CAST(SUM(t.amount) AS DECIMAL(18,2))   AS total_amount,
    CAST(AVG(t.amount) AS DECIMAL(18,2))   AS avg_amount,
    CAST(MAX(t.amount) AS DECIMAL(18,2))   AS max_amount
FROM iceberg.demo.AccountTransferAccount t
JOIN iceberg.demo.Account a ON t.fromId = a.accountId
WHERE t.createTime >= TIMESTAMP '2022-01-01 00:00:00'
  AND t.createTime <  TIMESTAMP '2023-01-01 00:00:00'
GROUP BY a.accountType
ORDER BY total_amount DESC;
```

## Modeling the Graph

Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
- Username: `puppygraph`
- Password: `puppygraph123`

This demo defaults to PuppyGraph `1.0-preview` with the v2 schema format. Both schemas include
local tables (called "local cache" in 0.x) for better query performance. Two schema files are
provided:

- **`schema-v2.json`** — v2 schema for PuppyGraph 1.x.
- **`schema-v1.json`** — v1 schema for PuppyGraph 0.x (e.g., 0.113). PuppyGraph `1.0-preview` also
  accepts v1 schemas and automatically converts them to v2 format when uploaded via the Web UI.

To upload the schema in PuppyGraph `1.0-preview`: go to the **Schema** page in the Web UI, click
**Upload Schema**, and select `schema-v2.json`. Choose **Cache data only** under **After Upload**.
For PuppyGraph 0.x, upload `schema-v1.json` instead.

Wait for the schema to be uploaded successfully and the local tables (or local cache) to be fully
loaded.

## Querying via PuppyGraph

Navigate to the **Query** panel on the left side. The **Graph Query** tab provides an interactive
environment for querying the graph using Gremlin and openCypher. 
After each query with graph visualization, remember to clear the graph panel before executing the next query to maintain a clean visualization. Click **Clear** at the top-right corner of the page.

Run a graph analytics query to find how much fund is gathered from accounts applying loans through
a specific person's multi-hop transfers — traverse 1-to-3 hops of account transfers within 2022 where each transfer amount is at least 1,000,000,
then find loans deposited into the destination accounts within the same time range and amount threshold.

First, visualize the overall transfer-to-loan pattern:

```cypher
MATCH p = (person:Person)-[edge1:PersonOwnAccount]->(account:Account)
          <-[edge2:AccountTransferAccount*1..3]-(other:Account)
          <-[edge3:LoanDepositAccount]-(loan:Loan)
WHERE elementId(person) = "Person[21990232556146]"
  AND ALL(e in edge2
      WHERE datetime("2022-01-01") < e.createTime < datetime("2023-01-01")
        AND e.amount >= 1000000)
  AND edge3.amount >= 1000000
  AND datetime("2022-01-01") < edge3.createTime < datetime("2023-01-01")
RETURN p
```

Then, aggregate to see how much each destination account received in loan deposits:

```cypher
MATCH (person:Person)-[edge1:PersonOwnAccount]->(account:Account)
      <-[edge2:AccountTransferAccount*1..3]-(other:Account)
WHERE elementId(person) = "Person[21990232556146]"
  AND ALL(e in edge2
      WHERE datetime("2022-01-01") < e.createTime < datetime("2023-01-01")
        AND e.amount >= 1000000)
WITH DISTINCT other
MATCH (other)<-[edge3:LoanDepositAccount]-(loan:Loan)
WHERE edge3.amount >= 1000000
  AND datetime("2022-01-01") < edge3.createTime < datetime("2023-01-01")
RETURN elementId(other) AS otherId,
       round(sum(edge3.amount), 2) AS sumDepositAmount
ORDER BY sumDepositAmount DESC
```

## Cleanup and Teardown

To stop and remove the containers and networks, run:

```bash
docker compose --env-file versions.env down -v
```
