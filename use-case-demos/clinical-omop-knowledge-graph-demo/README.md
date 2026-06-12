# MIMIC-OMOP Healthcare Graph Demo

## Summary

This demo illustrates how **PuppyGraph** enables complex multi-hop queries on healthcare data using the [MIMIC-IV demo data in the OMOP Common Data Model v0.9](https://physionet.org/content/mimic-iv-demo-omop/0.9/). The graph model allows healthcare analysts and researchers to:

- **Patient Journey Analysis:** Trace patient encounters across multiple visits, diagnoses, treatments, and measurements
- **Chronic Disease Management:** Identify patients with recurring conditions and high utilization patterns
- **Complex Care Patterns:** Find patients requiring both multiple diagnoses and procedures (e.g., surgical ICU patients)
- **Multi-Dimensional Analysis:** Discover complex patients with diverse healthcare interactions across conditions, medications, and measurements
- **Care Coordination:** Identify high-risk patients requiring coordinated care management

The system uses **PostgreSQL** as the data storage backend and **PuppyGraph** as the graph query engine, allowing seamless integration of relational healthcare data into a graph structure for powerful multi-hop analytics.

## Project Structure

```
├── README.md
├── docker-compose.yaml
├── schema.json
├── create_tables.sql
├── import_csv.sql
└── 1_omop_data_csv/       # Place MIMIC-IV OMOP CSV files here
```

## Prerequisites

- Docker & Docker Compose

## Deployment

1. Start PostgreSQL and PuppyGraph by running:
```bash
docker compose up -d
```

## Data Preparation

1. Download the MIMIC-IV demo data in OMOP Common Data Model v0.9 from PhysioNet:
   - Go to https://physionet.org/content/mimic-iv-demo-omop/0.9/
   - Scroll to the bottom of the page to find the data files
   - Download the CSV files and place them into the `1_omop_data_csv` directory.

2. Copy the downloaded data into the postgres container:
```bash
docker cp ./1_omop_data_csv postgres:/tmp/
```

3. From the `mimic-omop` project directory on the host machine, execute the SQL files to create tables and import data:  
```bash
docker exec -i postgres psql -U postgres -d mimic < ./create_tables.sql
docker exec -i postgres psql -U postgres -d mimic < ./import_csv.sql
```

## Modeling the Graph

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
   - Username: `puppygraph`
   - Password: `puppygraph123`

2. Upload the schema:
   - In the **Upload Graph Schema JSON** section, select the file `schema.json` and click **Upload**.
   - You can also upload the schema using `curl`:

        ```bash
        curl -XPOST -H "content-type: application/json" --data-binary @./schema.json --user "puppygraph:puppygraph123" localhost:8081/schema
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

## Graph Schema Reference

### Vertices (13)
- **Patient**: Person/patient records (from `person` table)
- **Visit**: Healthcare encounters/visits (from `visit_occurrence` table)
- **Condition**: Medical diagnoses and conditions (from `condition_occurrence` table)
- **Drug**: Medication exposures (from `drug_exposure` table)
- **Procedure**: Medical procedures and interventions (from `procedure_occurrence` table)
- **Measurement**: Clinical measurements and lab results (from `measurement` table)
- **Observation**: Clinical observations (from `observation` table)
- **Death**: Patient mortality information (from `death` table)
- **Concept**: Standardized clinical vocabulary and terminology mappings (from `concept` table)
- **Provider**: Healthcare providers (from `provider` table)
- **CareSite**: Healthcare facilities (from `care_site` table)
- **Location**: Geographic locations (from `location` table)
- **PayerPlan**: Insurance and payer coverage periods (from `payer_plan_period` table)

### Edges (18)

#### Clinical Journey Edges
- **visited**: Patient → Visit — Associates patients with their healthcare encounters
- **diagnosed_with**: Visit → Condition — Links visits to recorded diagnoses
- **prescribed**: Visit → Drug — Connects visits to medication exposures
- **underwent_procedure**: Visit → Procedure — Associates visits with medical procedures
- **measured**: Visit → Measurement — Links visits to clinical measurements and lab results
- **observed**: Visit → Observation — Connects visits to clinical observations

#### Provider and Facility Edges
- **treated_by**: Visit → Provider — Identifies the provider treating a patient during a visit
- **occurred_at**: Visit → CareSite — Links visits to the care facility where they occurred
- **employed_at**: Provider → CareSite — Associates providers with their employed facilities
- **located_at**: CareSite → Location — Links care sites to geographic locations

#### Patient Status Edges
- **died**: Patient → Death — Connects patients to mortality records
- **insured_by**: Patient → PayerPlan — Associates patients with insurance coverage periods

#### Terminology Mapping Edges
- **condition_is_concept**: Condition → Concept — Maps condition codes to standardized terminology
- **drug_is_concept**: Drug → Concept — Maps drug codes to standardized terminology
- **procedure_is_concept**: Procedure → Concept — Maps procedure codes to standardized terminology
- **measurement_is_concept**: Measurement → Concept — Maps measurement codes to standardized terminology
- **observation_is_concept**: Observation → Concept — Maps observation codes to standardized terminology
- **visit_is_concept**: Visit → Concept — Maps visit type codes to standardized terminology

## Data Notes

This demo uses MIMIC-IV data transformed to the OMOP CDM 5.3 format. The schema includes several modifications to handle MIMIC-IV-specific data requirements:

- **Column order reordered** to match CSV headers (PostgreSQL COPY maps by position, not column name)
- **ID fields use `bigint`** instead of `integer` (some MIMIC-IV person_id values exceed 32-bit range)
- **Numeric fields changed to `double precision`** for compatibility with MIMIC-IV data types
- **Varchar lengths increased** for fields with long values (e.g., `drug_source_value`, `specimen_source_id`)
- **Additional tables added** that are not in the standard OMOP CDM (e.g., `cohort`, `cohort_attribute`)
