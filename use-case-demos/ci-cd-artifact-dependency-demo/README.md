#  CI/CD Artifact Dependency Demo

## Summary
This demo showcases how PuppyGraph adeptly manages Artifact Dependency in software development environments.    
Through the graph, users can trace all direct and indirect dependencies of a specific artifact, understand the impact chains by identifying which other artifacts depend on it, and swiftly diagnose failing builds by correlating them with their dependencies.    
This comprehensive visibility accelerates troubleshooting, enhances build reliability, and supports developers in maintaining robust build pipelines within complex systems.

- **`README.md`**: Provides an overview of the project, including setup instructions and key details about the demo.
- **`docker-compose.yaml`**: Sets up the necessary services using Docker, defining containers and environments such as databases and applications for running the demo.
- **`CsvToParquet.py`**: Converts CSV files into Parquet format for easier data import into Iceberg.
- **`csv_data/`**:  Contains randomly generated CSV files representing artifacts, builds, dependencies, and deployments in a CI/CD environment.
                    These files serve as input for converting to Parquet format and subsequently importing into Iceberg to model the artifact dependency network.

## Prerequisites:
- Docker
- Docker Compose
- Python 3

## Data Preparation
- Convert CSV files to Parquet format:
```bash
python3 CsvToParquet.py ./csv_data ./parquet_data
```

## Deployment
- Start the Apache Iceberg services and PuppyGraph by running:
```bash
sudo docker compose up -d
```
Example output:
```bash
[+] Running 6/6
✔ Network puppy-iceberg         Created
✔ Container minio               Started
✔ Container mc                  Started
✔ Container iceberg-rest        Started
✔ Container spark-iceberg       Started
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
CREATE DATABASE cicd;

CREATE EXTERNAL TABLE cicd.Artifact (
  id            BIGINT,
  name          STRING,
  version       STRING,
  type          STRING,
  created_time  TIMESTAMP
) USING iceberg;

CREATE EXTERNAL TABLE cicd.Build (
  id            BIGINT,
  artifact_id   BIGINT,
  status        STRING,
  start_time    TIMESTAMP,
  end_time      TIMESTAMP
) USING iceberg;

CREATE EXTERNAL TABLE cicd.Dependency (
  id                BIGINT,
  from_artifact_id  BIGINT,
  to_artifact_id    BIGINT 
) USING iceberg;

CREATE EXTERNAL TABLE cicd.Deployment (
  id            BIGINT,
  artifact_id   BIGINT,
  environment   STRING,
  status        STRING,
  deployed_time TIMESTAMP
) USING iceberg;

INSERT INTO cicd.Artifact 
SELECT id,
       name, 
       version, 
       type,
       CAST(created_time AS TIMESTAMP)
FROM parquet.`/parquet_data/artifacts.parquet`;

INSERT INTO cicd.Build 
SELECT id,
       artifact_id, 
       status, 
       CAST(start_time AS TIMESTAMP),
       CAST(end_time AS TIMESTAMP)
FROM parquet.`/parquet_data/builds.parquet`;

INSERT INTO cicd.Dependency 
SELECT * FROM parquet.`/parquet_data/dependencies.parquet`;

INSERT INTO cicd.Deployment 
SELECT id,
       artifact_id, 
       environment, 
       status,
       CAST(deployed_time AS TIMESTAMP)
FROM parquet.`/parquet_data/deployments.parquet`;

```
- Exit the Spark-SQL shell:
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
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. You can do this by clicking the "Clear" button located in the top-right corner of the page.

Example Queries:
1. Query all direct and indirect dependencies of an artifact.
```gremlin
g.V("Artifact[1]")
  .repeat(__.out('DEPENDS_ON').simplePath())
  .emit()
  .times(6)
  .path()
```

2. Query which artifacts directly or indirectly depend on a certain artifact.
```gremlin
g.V("Artifact[830]")
  .repeat(__.in('DEPENDS_ON').simplePath())
  .emit()
  .times(6)
  .path()
```

3. Query the construction history of a certain artifact.
```gremlin
g.V("Artifact[1]").out('HAS_BUILD').path()
```

4. Query the deployment history of a certain artifact.
```gremlin
g.V("Artifact[1]").out('HAS_DEPLOYMENT').path()
```

5. Query all failing build records and dependencies related to a certain build.
```gremlin
g.V("Build[1439]")
  .in('HAS_BUILD').repeat(__.out('DEPENDS_ON').simplePath())
  .emit()
  .times(6)
  .out('HAS_BUILD').has('status', 'failure')
  .path()
```

## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
sudo docker compose down --volumes --remove-orphans
```
