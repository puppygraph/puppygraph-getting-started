# Open Threat Exchange (OTX) Demo

## Summary

This demo showcases real-time data analysis from Open Threat Exchange (OTX). The process involves:

- Downloading data via the OTX API.
- Storing the data in [PostgreSQL](https://docs.puppygraph.com/getting-started/querying-postgresql-data-as-a-graph/).
- Modeling the data as a graph.
- Querying with Cypher and Gremlin using PuppyGraph.

## Prerequisites

- [Docker and Docker Compose](https://docs.docker.com/compose/)
- [Python 3 and virtual environment](https://docs.python.org/3/library/venv.html)
- [OTX API KEY](https://otx.alienvault.com/api)

## Start the Services

Run the following command to start the services:

```bash
docker compose up -d
```

The services include:

- PostgreSQL
- PuppyGraph

## Creating a Python Virtual Environment

Set up and activate a virtual environment, then install the `psycopg2` binary package:

```bash
python3 -m venv myvenv
source myvenv/bin/activate
pip install psycopg2-binary
```

### Install OTX DirectConnect Python SDK (`OTXv2`)

This demo uses a **modified version** of `OTXv2`. 
The original SDK is from [AlienVault's official repo](https://github.com/AlienVault-OTX/OTX-Python-SDK), and modifications are documented in the [`NOTICE`](../OTX-Python-SDK/NOTICE) file.

```bash
cd ../OTX-Python-SDK
pip install .
```

After installing `OTXv2-1.5.12+mytest`, return to the demo directory.

## Create Data Tables in PostgreSQL

Access the PostgreSQL client:

```bash
docker exec -it postgres psql -h postgres -U postgres
```

When prompted, enter the password `postgres123` (as set in the Docker Compose file).

Run the SQL commands in `create_tables.sql` inside the PostgreSQL client.

Verify table creation with:

```sql
\d
```

## Download Pulse Data

Fill in your `API_KEY` in `data.py` and run:

```bash
python data.py download
```

This creates a `pulses` folder containing 100 JSON files.

According to the [OTX FAQ](https://otx.alienvault.com/faq), pulses provide threat intelligence, including:

- Threat summaries
- Indicators of compromise (IOCs)
- Targeted software details

## Import Data into PostgreSQL

Import the JSON pulse data into PostgreSQL:

```bash
python data.py import
```

Verify the import:

```sql
SELECT * FROM pulse LIMIT 5;
```

## Modeling the Graph

Log into the PuppyGraph Web UI at [http://localhost:8081](http://localhost:8081) with:

- **Username:** `puppygraph`
- **Password:** `puppygraph123`

Upload the schema:

- Under **Upload Graph Schema JSON**, select `schema.json` and click **Upload**.

## Querying via PuppyGraph

Navigate to **Query** in the Web UI:

- Use **Gremlin Query** for Gremlin queries with visualization (Cypher visualization is coming soon).
- Use **Graph Notebook** for Gremlin/Cypher queries.



### Example Queries
#### **Gremlin**

- **Number of pulses:**

  ```groovy
  g.V().hasLabel("pulse").count()
  ```

- **Max indicators linked to a pulse:**

  ```groovy
  g.V().hasLabel("pulse").local(__.out("pulse_indicator").count()).max()
  ```

- **Top 10 pulses by indicator count:**

  ```groovy
  g.V().hasLabel('pulse').as('p')
      .project('name', 'description', 'indicatorCount')
          .by('name')
          .by('description')
          .by(__.out('pulse_indicator').count())
      .order().by(select('indicatorCount'), desc)
      .limit(10)
  ```

- **Finds all indicator nodes with at least two incoming pulse_indicator edges and returns the corresponding paths as a subgraph:**
    ```groovy
    g.V().hasLabel("indicator")
      .where(__.in("pulse_indicator").count().is(gte(2)))
      .in("pulse_indicator").path()
    ```

#### **Cypher**

- **Number of pulses:**

  ```cypher
  MATCH (n:pulse) RETURN COUNT(n)
  ```

- **Max indicators linked to a pulse:**

  ```cypher
  MATCH (p:pulse)
  OPTIONAL MATCH (p)-[:pulse_indicator]->(i)
  WITH p, COUNT(i) AS indicatorCount
  RETURN max(indicatorCount) AS maxIndicatorCount
  ```

- **Top 10 pulses by indicator count:**

  ```cypher
  MATCH (p:pulse)
  OPTIONAL MATCH (p)-[:pulse_indicator]->(i)
  WITH p, COUNT(i) AS indicatorCount
  RETURN p.name, p.description, indicatorCount
  ORDER BY indicatorCount DESC
  LIMIT 10
  ```

- **Finds all indicator nodes with at least two incoming pulse_indicator edges and returns the corresponding paths as a subgraph:**
    ```cypher
    MATCH (i:indicator)<-[:pulse_indicator]-(p:pulse)
    WITH i, COUNT(p) AS pulseCount
    WHERE pulseCount >= 2
    MATCH path = (p)-[:pulse_indicator]->(i)
    RETURN path
    ```

## Cleanup and Teardown

Stop and remove the containers and networks:

```bash
docker compose down -v
```
