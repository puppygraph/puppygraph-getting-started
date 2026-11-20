# MIMIC-OMOP Healthcare Graph Demo (Unity Catalog + Delta Lake)

## Summary

This demo illustrates how **PuppyGraph** enables complex multi-hop queries on healthcare data using the [MIMIC-IV demo data in the OMOP Common Data Model v0.9](https://physionet.org/content/mimic-iv-demo-omop/0.9/). The graph model allows healthcare analysts and researchers to:

- **Patient Journey Analysis:** Trace patient encounters across multiple visits, diagnoses, treatments, and measurements
- **Chronic Disease Management:** Identify patients with recurring conditions and high utilization patterns
- **Complex Care Patterns:** Find patients requiring both multiple diagnoses and procedures (e.g., surgical ICU patients)
- **Multi-Dimensional Analysis:** Discover complex patients with diverse healthcare interactions across conditions, medications, and measurements
- **Care Coordination:** Identify high-risk patients requiring coordinated care management

The system uses **Unity Catalog** with **Delta Lake** tables, and **Apache Spark** for the initial writes. **PuppyGraph** is used as the graph query engine, allowing seamless integration of relational healthcare data into a graph structure for powerful multi-hop analytics.

A PostgreSQL version of this demo is available in [clinical-omop-knowledge-graph-demo](../clinical-omop-knowledge-graph-demo/).

## Project Structure

```
├── README.md
├── docker-compose.yaml
├── schema.json
├── create_tables.sql
├── import_csv.py
├── register.sh
└── 1_omop_data_csv/       # Place MIMIC-IV OMOP CSV files here
```

## Prerequisites

- Docker & Docker Compose

## Deployment

1. Start Unity Catalog, Apache Spark, and PuppyGraph by running:
```bash
docker compose up -d
```

## Data Preparation

1. Download the MIMIC-IV demo data in OMOP Common Data Model v0.9 from PhysioNet:
   - Go to https://physionet.org/content/mimic-iv-demo-omop/0.9/
   - Scroll to the bottom of the page to find the data files
   - Download the CSV files and place them into the `1_omop_data_csv` directory.

2. Copy the downloaded data into the Spark container:
```bash
docker cp ./1_omop_data_csv spark:/tmp/
```

3. From the `clinical-omop-unity-catalog-demo` project directory on the host machine, run the SQL script to create the tables and the Python script to import the data:
```bash
docker exec -i spark /opt/spark/bin/spark-sql < create_tables.sql
docker exec -i spark /opt/spark/bin/pyspark < import_csv.py
```

4. From the `clinical-omop-unity-catalog-demo` project directory on the host machine, execute the following Bash script to register the tables in Unity Catalog:
```bash
./register.sh
```

## Modeling the Graph

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
   - Username: `puppygraph`
   - Password: `puppygraph123`

2. Upload the schema:
   - In the **Upload Graph Schema JSON** section, select the file `schema.json` and click **Upload**. When prompted whether to cache data after upload, select **Cache data only**.
   - You can also upload the schema using `curl`. The `postUploadBehavior=load` parameter is the equivalent of **Cache data only**; without it the cached tables are created empty and queries return no rows:

        ```bash
        curl -XPOST -H "content-type: application/json" --data-binary @./schema.json --user "puppygraph:puppygraph123" "localhost:8081/schema?postUploadBehavior=load"
        ```

## Querying the Graph using Cypher

Navigate to the Query panel on the left side. The Graph Query tab offers an interactive environment for querying the graph using Cypher and Gremlin.

After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. You can do this by clicking the "Clear Canvas" button located in the top-right corner of the page.

### Example Cypher Queries

#### 1. Patient Journey - Recurring Conditions Analysis

Find patients who have been diagnosed with the same condition multiple times (5+ occurrences), revealing chronic disease patterns:

```cypher
MATCH (p:Patient)-[:visited]->(v:Visit)-[:diagnosed_with]->(c:Condition)
WITH p, c.condition_concept_id AS concept_id, count(DISTINCT c) AS occurrence_count
WHERE occurrence_count >= 5
RETURN p.person_id AS patient_id, concept_id, occurrence_count
ORDER BY occurrence_count DESC
LIMIT 50
```

#### 2. Complex Care Pattern Analysis

Identify patients with both multiple conditions (5+) AND multiple procedures (5+), revealing surgical and interventional cases:

```cypher
MATCH (p:Patient)-[:visited]->(v1:Visit)-[:diagnosed_with]->(c:Condition)
MATCH (p)-[:visited]->(v2:Visit)-[:underwent_procedure]->(proc:Procedure)
WITH p, count(DISTINCT c) AS condition_count, count(DISTINCT proc) AS procedure_count
WHERE condition_count >= 5 AND procedure_count >= 5
RETURN p.person_id AS patient_id, condition_count, procedure_count,
       (condition_count + procedure_count) AS total_clinical_events
ORDER BY total_clinical_events DESC
LIMIT 20
```

#### 3. Multi-Dimensional Patient Analysis

Find the most complex patients with diverse healthcare interactions across three dimensions:

```cypher
MATCH (p:Patient)-[:visited]->(v1:Visit)-[:diagnosed_with]->(c:Condition)
WITH p, count(DISTINCT c) AS condition_count
MATCH (p)-[:visited]->(v2:Visit)-[:prescribed]->(d:Drug)
WITH p, condition_count, count(DISTINCT d) AS drug_count
MATCH (p)-[:visited]->(v3:Visit)-[:measured]->(m:Measurement)
WITH p, condition_count, drug_count, count(DISTINCT m) AS measurement_count
WHERE condition_count >= 3 AND drug_count >= 10 AND measurement_count >= 100
RETURN p.person_id AS patient_id, condition_count, drug_count, measurement_count
ORDER BY measurement_count DESC
LIMIT 20
```

## Cleanup and Teardown

To stop and remove the containers, networks, and volumes, run:
```bash
docker compose down -v
```
