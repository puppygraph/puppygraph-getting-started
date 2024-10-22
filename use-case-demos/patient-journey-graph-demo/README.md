#  Patient Journey Graph Demo

## Summary
This demo queries the public MIMIC Demo Dataset on patient journey usually needed by healthcare or insurance organizations.
It also demonstrates users can query the same copy of data both in SQL (via Trino) and Graph (via PuppyGraph).

- **`README.md`**: Provides an overview of the project, including setup instructions and key details about the demo.
- **`docker-compose.yaml`**: Sets up the necessary services using Docker, defining containers and environments such as databases and applications for running the demo.
- **`CsvToParquet.py`**: Converts MIMIC-IV Demo CSV files into Parquet format to optimize data loading into Iceberg tables.
- **`trino-catalog/`**: Contains configuration files for Trino, which define how Trino connects to the Iceberg catalog and queries data.


## Prerequisites:
- Docker
- Docker Compose
- Python 3
- wget (for downloading data)
- gunzip (for decompressing data)


## Note:
The steps below provide a demonstration using sample data from the MIMIC-IV Demo dataset. 
In real-world use cases, you can directly connect your existing data sources to PuppyGraph, bypassing the sample data preparation step.

## Demo Data Preparation
- Download MIMIC-IV Clinical Dataset
```bash
mkdir -p csv_data
wget -O csv_data/admissions.csv.gz "https://physionet.org/files/mimic-iv-demo/2.2/hosp/admissions.csv.gz?download"
wget -O csv_data/d_icd_diagnoses.csv.gz "https://physionet.org/files/mimic-iv-demo/2.2/hosp/d_icd_diagnoses.csv.gz?download"
wget -O csv_data/diagnoses_icd.csv.gz "https://physionet.org/files/mimic-iv-demo/2.2/hosp/diagnoses_icd.csv.gz?download"
wget -O csv_data/patients.csv.gz "https://physionet.org/files/mimic-iv-demo/2.2/hosp/patients.csv.gz?download"
wget -O csv_data/provider.csv.gz "https://physionet.org/files/mimic-iv-demo/2.2/hosp/provider.csv.gz?download"
```

- Unzip the downloaded file
```bash
gunzip csv_data/*.csv.gz
```

- Convert CSV files to Parquet format:
```bash
python3 CsvToParquet.py ./csv_data ./parquet_data
```

## Deployment
- Start the Apache Iceberg services, PuppyGraph, Trino by running:
```bash
sudo docker compose up -d
```
Example output:
```bash
[+] Running 6/6
✔ Network puppy-iceberg         Created
✔ Container minio               Started
✔ Container iceberg-rest        Started
✔ Container spark-iceberg       Started
✔ Container mc                  Started
✔ Container trino               Started
✔ Container puppygraph          Started
```

## Data Import
- Start the Spark-SQL shell to access Iceberg:
```bash
sudo docker exec -it spark-iceberg spark-sql
```
The shell prompt will appear as:
```shell
spark-sql ()>
```

- Execute the following SQL commands to create tables and import data:
```sql
CREATE DATABASE mimiciv_hosp;

CREATE EXTERNAL TABLE mimiciv_hosp.admissions (
  subject_id            INT,
  hadm_id               INT,
  admittime             TIMESTAMP,
  dischtime             TIMESTAMP,
  deathtime             TIMESTAMP,
  admission_type        STRING,
  admit_provider_id     STRING,
  admission_location    STRING,
  discharge_location    STRING,
  insurance             STRING,
  language              STRING,
  marital_status        STRING,
  race                  STRING,
  edregtime             TIMESTAMP,
  edouttime             TIMESTAMP,
  hospital_expire_flag  INT
) USING iceberg;

CREATE EXTERNAL TABLE mimiciv_hosp.d_icd_diagnoses (
  icd_code      STRING,
  icd_version   INT,
  long_title    STRING,
  icd_code_full STRING
) USING iceberg;

CREATE EXTERNAL TABLE mimiciv_hosp.diagnoses_icd (
  subject_id    INT,
  hadm_id       INT,
  seq_num       INT,
  icd_code      STRING,
  icd_version   INT,
  icd_code_full STRING,
  unique_id     STRING
) USING iceberg;

CREATE EXTERNAL TABLE mimiciv_hosp.patients (
  subject_id        INT,
  gender            STRING,
  anchor_age        INT,
  anchor_year       INT,
  anchor_year_group STRING,
  dod               DATE
) USING iceberg;

CREATE EXTERNAL TABLE mimiciv_hosp.provider (
  provider_id STRING
) USING iceberg;

INSERT INTO mimiciv_hosp.admissions 
SELECT subject_id, 
       hadm_id,
       CAST(admittime AS TIMESTAMP), 
       CAST(dischtime AS TIMESTAMP),
       CAST(deathtime AS TIMESTAMP),
       admission_type,
       admit_provider_id,
       admission_location,
       discharge_location,
       insurance,
       language,
       marital_status,
       race,
       CAST(edregtime AS TIMESTAMP),
       CAST(edouttime AS TIMESTAMP),
       hospital_expire_flag
FROM parquet.`/parquet_data/admissions.parquet`;

INSERT INTO mimiciv_hosp.d_icd_diagnoses 
SELECT icd_code, 
       icd_version,
       long_title,
       icd_code || '_' || icd_version as icd_code_full
FROM parquet.`/parquet_data/d_icd_diagnoses.parquet`;

INSERT INTO mimiciv_hosp.diagnoses_icd 
SELECT subject_id, 
       hadm_id,
       seq_num,
       icd_code,
       icd_version,
       icd_code || '_' || icd_version as icd_code_full,
       hadm_id || '_' || seq_num as unique_id
FROM parquet.`/parquet_data/diagnoses_icd.parquet`;

INSERT INTO mimiciv_hosp.patients 
SELECT subject_id, 
       gender,
       anchor_age,
       anchor_year,
       anchor_year_group,
       CAST(dod AS DATE)
FROM parquet.`/parquet_data/patients.parquet`;

INSERT INTO mimiciv_hosp.provider 
SELECT * FROM parquet.`/parquet_data/provider.parquet`;

```
- Exit the Spark-SQL shell:
```sql
quit;
```

## Trino Section
1. Enter into trino container and start trino-cli
```bash
sudo docker exec -it trino bash
trino --server localhost:8080 --catalog iceberg --schema mimiciv_hosp
```
The shell prompt will appear as:
```sql
trino:mimiciv_hosp>
```

## Modeling the Graph
1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
- Username: `puppygraph`
- Password: `puppygraph123`

2. Upload the schema:
- Select the file `schema.json` in the Upload Graph Schema JSON section and click on Upload.


## Querying the Graph using Gremlin and Trino
- Navigate to the Query panel on the left side. The Gremlin Query tab offers an interactive environment for querying the graph using Gremlin.
- After each gremlin query, remember to clear the graph panel before executing the next query to maintain a clean visualization. 
  You can do this by clicking the "Clear" button located in the top-right corner of the page.

Example Queries:
1. Query the information of the first 10 patients.
- trino client shell
```sql
select * from patients order by subject_id limit 10;
```

- Gremlin Query
```gremlin
g.V().hasLabel('patient')
  .order()
  .by('subject_id')
  .limit(10)
```

2. Query the complete path from a specific patient to their related admissions, diagnoses, and the corresponding ICD diagnosis details.
- trino client shell
```sql
SELECT p.subject_id AS patient_id, 
       a.hadm_id AS admission_id, 
       d.unique_id AS diagnosis_id, 
       dim.icd_code_full AS icd_code_full
FROM patients p
JOIN admissions a ON p.subject_id = a.subject_id
JOIN diagnoses_icd d ON a.hadm_id = d.hadm_id
JOIN d_icd_diagnoses dim ON d.icd_code_full = dim.icd_code_full
WHERE p.subject_id = 10000032;
```

- Gremlin Query
```gremlin
g.V("patient[10000032]")
  .out('admitted_to')
  .out('diagnosed_as')
  .out('belongs_dim')
  .path()
```

3. Modify data through trino and read data using puppy
- Query a specific patient
  - trino client shell
  ```sql
  SELECT * FROM patients WHERE subject_id = 10000032;
  ```
  - Gremlin Query
  ```gremlin
  g.V("patient[10000032]").elementMap()
  ```
  
- Modify this patient data through trino
  - trino client shell
  ```sql
  UPDATE patients SET anchor_age=99 WHERE subject_id = 10000032;
  ```

- Query the specific patient again
  - trino client shell
  ```sql
  SELECT * FROM patients WHERE subject_id = 10000032;
  ```
  - Gremlin Query
  ```gremlin
  g.V("patient[10000032]").elementMap()
  ```
  
4. query all patients diagnosed with "Aphasia" and then to find their other diagnosis records.
- Gremlin Query
```gremlin
g.V().hasLabel('dim_diagnosis').has('long_title', 'Aphasia')
  .in('belongs_dim').as('c1')
  .in('diagnosed_as').in('admitted_to').as('p')
  .out('admitted_to').as('e1')
  .out('diagnosed_as').as('d2')
  .out('belongs_dim').as('c2')
  .where(neq('c1'))
  .path()
```

## Cleanup and Teardown
- Exit trino-cli shell
```sql
exit
```
- Exit trino container
```bash
exit
```
- This command will stop and remove all running containers related to PuppyGraph, Trino, Spark, and MinIO.
```bash
sudo docker compose down --volumes --remove-orphans
```
