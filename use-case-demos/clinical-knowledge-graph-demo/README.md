#  Clinical Knowledge Graph Demo

## Summary
This demo showcases how PuppyGraph leverages the rich [Drug Central](https://drugcentral.org/) dataset to enhance pharmaceutical research.  
By querying across diverse data stores like Iceberg and PostgreSQL, users can retrieve FDA-approved drugs and explore mechanisms of action on human targets.  
These capabilities support faster, more informed decision-making in drug discovery by providing real-time access to comprehensive drug information.

- **`README.md`**: Provides an overview of the project, including setup instructions and key details about the demo.
- **`docker-compose.yaml`**: Sets up the necessary services using Docker, defining containers and environments such as databases and applications for running the demo.
- **`CsvToParquet.py`**: Converts CSV files into Parquet format for easier data import into Iceberg.
- **`sql_data/`**:  Contains PostgreSQL database dump files and SQL scripts to create views for the graph.

## Prerequisites:
- Docker
- Docker Compose
- Python 3

## Note:
The following Data Download and Import steps populate example data for this demo.
For real-world applications, you can connect PuppyGraph to your existing data sources directly, bypassing these steps

## Data Download
- Download Drug Central data
```bash
wget -P ./sql_data https://unmtid-shinyapps.net/download/drugcentral.dump.11012023.sql.gz
```
- Unzip the downloaded file:
```bash
gunzip ./sql_data/drugcentral.dump.11012023.sql.gz
```

## Deployment
- Start the Apache Iceberg services, PuppyGraph, PostgreSQL by running:
```bash
sudo docker compose up -d
```
Example output:
```bash
[+] Running 6/6
✔ Network puppy-iceberg         Created
✔ Container minio               Started
✔ Container postgres            Started
✔ Container mc                  Started
✔ Container iceberg-rest        Started
✔ Container spark-iceberg       Started
✔ Container puppygraph          Started
```

## Data Import
1. Enter into PostgreSQL shell.
```bash
docker exec -it postgres psql -U postgres
```

2. Import Drug Central data into postgres.
```sql
\i /sql_data/drugcentral.dump.11012023.sql
```
```sql
\c postgres
```

3. Create postgresql views for graph.
```sql
\i /sql_data/puppy_views.sql
```

4. Export some postgresql tables to the corresponding Parquet file.
```sql
\COPY approval TO '/sql_data/approval.csv' DELIMITER ',' CSV HEADER;
\COPY inn_stem TO '/sql_data/inn_stem.csv' DELIMITER ',' CSV HEADER;
```

5. Exit PostgreSQL shell
```
\q
```

6. Convert CSV files to Parquet format:
```bash
sudo python3 CsvToParquet.py ./sql_data ./parquet_data
```

7. Start the Spark-SQL shell to access Iceberg:
```bash
sudo docker exec -it spark-iceberg spark-sql
```
The shell prompt will appear as:
```shell
spark-sql ()>
```

8. Execute the following SQL commands to create tables and import data to Iceberg:
```sql
CREATE DATABASE drugdb;

CREATE EXTERNAL TABLE drugdb.approval (
  id        INT,
  struct_id INT,
  approval  DATE,
  type      STRING,
  applicant STRING,
  orphan    BOOLEAN
) USING iceberg;

CREATE EXTERNAL TABLE drugdb.inn_stem (
  id            INT,
  stem          STRING,
  definition    STRING,
  national_name STRING,
  length        INT,
  discontinued  BOOLEAN
) USING iceberg;

INSERT INTO drugdb.approval 
SELECT id,
       struct_id, 
       CAST(approval AS DATE),
       type, 
       applicant,
       CAST(orphan AS BOOLEAN)
FROM parquet.`/parquet_data/approval.parquet`;

INSERT INTO drugdb.inn_stem
SELECT id,
       stem, 
       definition,
       national_name, 
       length,
       CAST(discontinued AS BOOLEAN)
FROM parquet.`/parquet_data/inn_stem.parquet`;

```
9. Exit the Spark-SQL shell
```sql
quit;
```

## Modeling the Graph
1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
- Username: `puppygraph`
- Password: `puppygraph123`

2. Upload the schema:
- Select the file `schema.json` in the Upload Graph Schema JSON section and click on Upload.

## Querying the Graph

- Navigate to the Query panel on the left side. The **Graph Query** tab offers an interactive environment for querying the graph using Gremlin and openCypher.
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. 
  You can do this by clicking the "Clear" button located in the top-right corner of the page.

Example Queries:
1. Query the drugs approved by FDA, limiting the number of returned results.
```gremlin
g.V().hasLabel('Approval').has('type', 'FDA')
  .out('APPROVE')
  .hasLabel('Drug')
  .dedup()
  .limit(10)
```

2. Query all FDA approved drugs with 1 or more currently marketed formulation
```gremlin
g.V().hasLabel('Drug')
  .has('no_formulations', gt(0))
  .valueMap()
```

3. Query mechanism of action targets for human targets only.
```gremlin
g.V().hasLabel('Drug').as('d')
  .out('HAS_BIOACTIVITY').has('moa', 1).has('organism', 'Homo sapiens').as('a')
  .out('TARGET_TO').as('t')
  .project('DrugID', 'DrugName', 'TargetName', 'TargetClass', 'accession', 'gene', 'swissprot', 'actValue')
    .by(select('d').id())
    .by(select('d').values('name'))
    .by(select('t').values('name'))
    .by(select('t').values('target_class'))
    .by(select('a').values('accession'))
    .by(select('a').values('gene'))
    .by(select('a').values('swissprot'))
    .by(select('a').values('act_value'))
```

4. Query all significant adverse events associated with Atorvastatin from FDA FAERS database based on likelihood ratio test.
```gremlin
g.V().has('Drug', 'name', 'atorvastatin')
  .outE('HAS_ADVERSEEVENT_ALL')
  .has('llr').has('llr_threshold').as('a')
  .inV().as('f')
  .where('a', gt('a')).by('llr').by('llr_threshold')
  .project('meddraName', 'meddraCode', 'llr', 'llrThreshold')
    .by(select('f').values('meddra_name'))
    .by(select('f').id())
    .by(select('a').values('llr'))
    .by(select('a').values('llr_threshold'))
    .order()
    .by('llr')
```

5. Find drug has same class but different stem with atovastatin which is not exclusive.
```gremlin
g.V().hasLabel('Stem').as('s1')
  .in('HAS_STEM').has('name', 'atorvastatin').as('d')
  .out('DRUG_BELONGS_TO').in('DRUG_BELONGS_TO').as('d2')
  .out('HAS_STEM').as('s2')
  .select('s1', 's2')
  .where('s1', neq('s2'))
  .select('d2')
  .out('RECORD_IN_ORANGEBOOK')
  .not(out('HAS_EXCLUSIVITY'))
  .select('d2')
  .dedup()
  .values('name')
```



## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
sudo docker compose down --volumes --remove-orphans
```
