#  Cloud Security Graph Demo

## Summary
This demo demonstrates a robust pipeline for build SIEM-like investigation graphs, processing and analyzing cloud security logs in a complex cloud environment. 
The system dynamically reads multiple JSON log files from a designated directory (json_log), processes them into unified structured files, converts these to Parquet format, and then imports the data into Apache Iceberg to model the security graph.
We use a public dataset of anonymized AWS CloudTrail logs from [flaws.cloud](https://summitroute.com/blog/2020/10/09/public_dataset_of_cloudtrail_logs_from_flaws_cloud/), a security training environment created by Scott Piper. It contains 1.9 million events simulating realistic attack scenarios in AWS—ideal for modeling real-world threat investigations.


## Project Structure
- **`README.md`**: Provides an overview of the project, including setup instructions and key details about the demo.
- **`docker-compose.yaml`**: Sets up the necessary services using Docker, defining containers and environments such as databases and applications for running the demo.
- **`json_to_parquet.py`**: Converts JSON files into Parquet format for easier data import into Iceberg.
- **`schema.json`**: Defines the graph schema from the relational data, including the catalog and nodes and relationships, for the PuppyGraph application.

## Prerequisites:
- Docker and Docker Compose
- Python 3

## Note:
The Demo Data Preparation step below populates some example data for demonstration purposes. 
For real-world use cases, you can directly connect your existing data sources to PuppyGraph without the need for data preparation. 
In other words, you can either download and use publicly available sample data or apply your own real-world datasets.

## Data Preparation
1. Download and Extract the Log File
```
wget https://summitroute.com/downloads/flaws_cloudtrail_logs.tar
mkdir -p ./json_data
tar -xvf flaws_cloudtrail_logs.tar --strip-components=1 -C ./json_data
gunzip ./json_data/*.json.gz
```

2. We will create a virtual environment and run the python script `json_to_parquet.py` to convert JSON files to Parquet format. On some Linux distributions, you may need to install `python3-venv` first.
```bash
# On some Linux distributions, install `python3-venv` first.
sudo apt-get update
sudo apt-get install python3-venv
```

- Create a virtual environment, activate it and install the necessary packages.
```bash
python3 -m venv demo_venv
source demo_venv/bin/activate
pip install pandas pyarrow ijson faker
```

- Convert JSON files to Parquet format:
```bash
python3 json_to_parquet.py ./json_data ./parquet_data
```

## Deployment
- Start the Apache Iceberg services and PuppyGraph by running:
```bash
docker compose up -d
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
docker exec -it spark-iceberg spark-sql
```
The shell prompt will appear as:
```shell
spark-sql ()>
```

- Execute the following SQL commands to create tables and import data:
```sql
CREATE DATABASE security_graph;

CREATE EXTERNAL TABLE security_graph.Account (
  account_id            STRING,
  account_alias         STRING,
  email                 STRING,
  phone                 STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.Identity (
  identity_id           STRING,
  type                  STRING,
  principal_id          STRING,
  arn                   STRING,
  user_name             STRING, 
  account_id            STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.Session (
  session_id            STRING,
  creation_date         TIMESTAMP,
  mfa_authenticated     BOOLEAN,
  additional_info       STRING,
  identity_id           STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.Event (
  event_id              STRING,
  event_time            TIMESTAMP,
  event_source          STRING,
  event_name            STRING,
  source_ip             STRING,
  user_agent            STRING,
  request_params        STRING,
  response_params       STRING,
  identity_id           STRING,
  session_id            STRING,
  account_id            STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.Resource (
  resource_id           STRING,
  resource_name         STRING,
  resource_type         STRING,
  additional_metadata   STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.EventResource (
  event_id              STRING,
  resource_id           STRING,
  pre_state             STRING,
  post_state            STRING
) USING iceberg;
       
INSERT INTO security_graph.Account
SELECT * FROM parquet.`/parquet_data/Account.parquet`;

INSERT INTO security_graph.Identity
SELECT * FROM parquet.`/parquet_data/Identity.parquet`;

INSERT INTO security_graph.Session
SELECT
    session_id,
    CAST(creation_date AS TIMESTAMP),
    mfa_authenticated,
    additional_info,
    identity_id
FROM parquet.`/parquet_data/Session.parquet`;

INSERT INTO security_graph.Event
SELECT
    event_id,
    CAST(event_time AS TIMESTAMP),
    event_source,
    event_name,
    source_ip,
    user_agent,
    request_params,
    response_params,
    identity_id,
    session_id,
    CAST(account_id AS STRING) as account_id
FROM parquet.`/parquet_data/Event.parquet`;

INSERT INTO security_graph.Resource
SELECT * FROM parquet.`/parquet_data/Resource.parquet`;

INSERT INTO security_graph.EventResource
SELECT * FROM parquet.`/parquet_data/EventResource.parquet`;

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

- Navigate to the Query panel on the left side. The Graph Query tab offers an interactive environment for querying the graph using Gremlin and Cypher.
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. 
  You can do this by clicking the "Clear Canvas" button located in the top-right corner of the page.

Example Queries:
1. Find the Full Chain from Account to Resource.
```cypher
MATCH (a:Account)-[:HasIdentity]->(i:Identity)-[:HasSession]->(s:Session)-[:RecordsEvent]->(e:Event)-[:OperatesOn]->(r:Resource)
RETURN a.account_id AS Account,
       i.identity_id AS Identity,
       s.session_id AS Session,
       e.event_id AS Event,
       r.resource_name AS Resource,
       r.resource_type AS ResourceType
LIMIT 50
```

```gremlin
g.V().hasLabel('Account').as('a')
  .out('HasIdentity').hasLabel('Identity').as('i')
  .out('HasSession').hasLabel('Session').as('s')
  .out('RecordsEvent').hasLabel('Event').as('e')
  .out('OperatesOn').hasLabel('Resource').as('r')
  .select('a', 'i', 's', 'e', 'r')
  .by(valueMap('account_id').unfold())
  .by(valueMap('identity_id').unfold())
  .by(valueMap('session_id').unfold())
  .by(valueMap('event_id').unfold())
  .by(valueMap('resource_name').unfold())
  .by(valueMap('resource_type').unfold())
  .limit(50)
```

2. Count Events per Account in a Specific Time Range.
```cypher
MATCH (a:Account)-[:HasIdentity]->()-[:HasSession]->(s:Session)-[:RecordsEvent]->(e:Event)
WHERE e.event_time >= datetime("2017-02-01T00:00:00") 
  AND e.event_time < datetime("2017-03-01T00:00:00")
RETURN a.account_id AS Account, count(e) AS EventCount
ORDER BY EventCount DESC
```

```gremlin
g.V().hasLabel('Account').as('a')
  .out('HasIdentity')
  .out('HasSession').hasLabel('Session').as('s')
  .out('RecordsEvent').hasLabel('Event').as('e')
  .where(__.values('event_time').is(P.gte('2017-02-01 00:00:00')))
  .where(__.values('event_time').is(P.lt('2017-03-01 00:00:00')))
  .group().by(select('a').by('account_id'))
    .by(count())
  .unfold()
  .order().by(values, desc)
  .project('Account', 'EventCount')
    .by(keys)
    .by(values)
```

3. Identify Accounts Operating on a Specific Resource Type.
```cypher
MATCH (a:Account)-[:HasIdentity]->(i:Identity)-[:HasSession]->(s:Session)-[:RecordsEvent]->(e:Event)-[:OperatesOn]->(r:Resource)
WHERE r.resource_type = 's3bucket'
RETURN a.account_id AS Account,
       r.resource_name AS S3BucketName,
       e.event_id AS EventID
LIMIT 50
```

```gremlin
g.V().hasLabel('Account').as('a')
  .out('HasIdentity').hasLabel('Identity').as('i')
  .out('HasSession').hasLabel('Session').as('s')
  .out('RecordsEvent').hasLabel('Event').as('e')
  .out('OperatesOn').hasLabel('Resource').as('r')
  .has('resource_type', 's3bucket')
  .select('a', 'r', 'e')
  .by(valueMap('account_id').unfold())
  .by(valueMap('resource_name').unfold())
  .by(valueMap('event_id').unfold())
  .limit(50)
```

4. Retrieve Detailed Multi-Hop Paths for EC2 Instances.
```cypher
MATCH path = (a:Account)-[:HasIdentity]->(i:Identity)-[:HasSession]->(s:Session)-[:RecordsEvent]->(e:Event)-[:OperatesOn]->(r:Resource)
WHERE r.resource_type = 'ec2instance'
RETURN path
LIMIT 25
```

```gremlin
g.V().hasLabel('Account').as('a')
  .out('HasIdentity').hasLabel('Identity').as('i')
  .out('HasSession').hasLabel('Session').as('s')
  .out('RecordsEvent').hasLabel('Event').as('e')
  .out('OperatesOn').hasLabel('Resource').as('r')
  .has('resource_type', 'ec2instance')
  .path()
  .limit(25)
```


## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
docker compose down --volumes --remove-orphans
```
