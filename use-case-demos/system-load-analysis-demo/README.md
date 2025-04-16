#  System Load Analysis Demo

## Summary
This demo showcases how to analyze and visualize high CPU utilization across components within a large call graph, using PuppyGraph's powerful query capabilities.  
By querying historical records related to components with a CPU load ratio above 0.9, users can swiftly identify patterns of heavy usage and the associated component and invocation information.   
Additionally, the application of the PageRank algorithm ranks the importance of each component, providing insights into which components are critical within the network and might need optimization or monitoring to prevent system overloads.   
This practical approach helps in proactive system maintenance and optimization in complex environments.

- **`README.md`**: Provides an overview of the project, including setup instructions and key details about the demo.
- **`docker-compose.yaml`**: Sets up the necessary services using Docker, defining containers and environments such as databases and applications for running the demo.
- **`CsvToParquet.py`**: Converts CSV files into Parquet format for easier data import into Iceberg.
- **`csv_data/`**:  Contains randomly generated CSV files representing components, their history, and invocations within a system's call graph. 
                    These files are used as input for converting to Parquet format and then imported into Iceberg to model the system's load analysis and invocation network.

## Prerequisites:
- Docker
- Docker Compose
- Python 3

## Note:
The Data Preparation and Data Import steps below populate some example data for demonstration purposes. 
For real-world use cases, you can directly connect your existing data sources to PuppyGraph without the need for data preparation.

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
CREATE DATABASE big_call_graph;

CREATE EXTERNAL TABLE big_call_graph.Component (
  id                BIGINT,
  name              STRING,
  version           STRING,
  type              STRING,
  cpu_usage         DOUBLE,
  mem_usage         DOUBLE,
  network_bandwidth DOUBLE
) USING iceberg;

CREATE EXTERNAL TABLE big_call_graph.ComponentHistory (
  id                BIGINT,
  component_id      BIGINT,
  record_time       TIMESTAMP,
  cpu_usage         DOUBLE,
  mem_usage         DOUBLE,
  network_bandwidth DOUBLE,
  parent_id         BIGINT
) USING iceberg;

CREATE EXTERNAL TABLE big_call_graph.Invocation (
  id            BIGINT,
  from_com_id   BIGINT,
  to_com_id     BIGINT,
  req_time      TIMESTAMP,
  res_time      TIMESTAMP,
  status        STRING,
  err_msg       STRING,
  parent_id     BIGINT,
  history_id    BIGINT
) USING iceberg;

CREATE EXTERNAL TABLE big_call_graph.ComponentInvocationCount (
  id                BIGINT,
  from_com_id       BIGINT,
  to_com_id         BIGINT,
  invocate_times    INT
) USING iceberg;

INSERT INTO big_call_graph.Component 
SELECT * FROM parquet.`/parquet_data/Component.parquet`;

INSERT INTO big_call_graph.ComponentHistory 
SELECT id,
       component_id, 
       CAST(record_time AS TIMESTAMP),
       cpu_usage, 
       mem_usage,
       network_bandwidth,
       parent_id
FROM parquet.`/parquet_data/ComponentHistory.parquet`;

INSERT INTO big_call_graph.Invocation 
SELECT id,
       from_com_id, 
       to_com_id, 
       CAST(req_time AS TIMESTAMP),
       CAST(res_time AS TIMESTAMP),
       status, 
       err_msg,
       parent_id,
       history_id
FROM parquet.`/parquet_data/Invocation.parquet`;

INSERT INTO big_call_graph.ComponentInvocationCount
SELECT 
    ROW_NUMBER() OVER (ORDER BY from_com_id, to_com_id) AS id,
    from_com_id,
    to_com_id,
    COUNT(*) as invocate_times
FROM parquet.`/parquet_data/Invocation.parquet`
GROUP BY from_com_id, to_com_id;

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
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. 
  You can do this by clicking the "Clear" button located in the top-right corner of the page.

Example Queries:
1. Query historical records of CPU load ratio greater than 0.9, as well as related components and invocations.
```gremlin
g.V().hasLabel('ComponentHistory')
  .has('cpu_usage', gt(0.9))
  .in('InvocationHis')
  .out('InvocationTo')
  .path()
```

2. Query the direct and indirect invocation information of high CPU load ratio record.
```gremlin
g.V().hasLabel('ComponentHistory')
  .has('cpu_usage', gt(0.998))
  .in('InvocationHis')
  .repeat(out('InvocationStack').simplePath())
  .emit()
  .path()
```

3. Rank the importance of each component using the PageRank algorithm based on the topology and frequency of invocations.
```cypher
CALL algo.paral.pagerank({labels: ['Component'], relationshipTypes: ['HasInvocation'], relationshipWeightProperty: 'invocate_times', dampingFactor: 0.85}) YIELD id, score RETURN id, score ORDER BY score DESC
```

## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
sudo docker compose down --volumes --remove-orphans
```
