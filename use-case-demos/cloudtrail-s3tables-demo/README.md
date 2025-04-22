#  Cloud Security Graph Demo

## Summary
This demo shows how to build a SIEM-like investigation graph directly on Amazon S3 Tables using PuppyGraph. We use a public dataset of anonymized AWS CloudTrail logs from [flaws.cloud](https://summitroute.com/blog/2020/10/09/public_dataset_of_cloudtrail_logs_from_flaws_cloud/), a security training environment created by Scott Piper. It contains 1.9 million events simulating realistic attack scenarios in AWS—ideal for modeling real-world threat investigations.

## Prerequisites:
- Docker
- Python 3
- Apache Spark
- AWS CLI

## Note:
The Demo Data Preparation step below populates some example data for demonstration purposes. 
For real-world use cases, you can directly connect your existing data sources to PuppyGraph without the need for data preparation. 
In other words, you can either download and use publicly available sample data or apply your own real-world datasets.

## Data Preparation
1. Create table bucket
```
aws s3tables create-table-bucket \
    --region <region> \
    --name security-demo
```
- Create namespace
```
aws s3tables create-namespace \
    --table-bucket-arn <table-bucket-arn> \
    --namespace security_graph
```
2. Download and Extract the Log File
```
wget https://summitroute.com/downloads/flaws_cloudtrail_logs.tar
mkdir -p ./json_data
tar -xvf flaws_cloudtrail_logs.tar --strip-components=1 -C ./json_data
gunzip ./json_data/*.json.gz
```

3. We will create a virtual environment and run the python script `import_from_json.py`. On some Linux distributions, you may need to install `python3-venv` first.
```bash
# On some Linux distributions, install `python3-venv` first.
sudo apt-get update
sudo apt-get install python3-venv
```

- Create a virtual environment, activate it and install the necessary packages.
```bash
python3 -m venv demo_venv
source demo_venv/bin/activate
pip install ijson faker pyspark
```

3. Import JSON data to S3 Tables
```bash
spark-submit \
  --master "local[*]" \
  --packages "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.1,software.amazon.awssdk:bundle:2.20.160,software.amazon.awssdk:url-connection-client:2.20.160" \
  --conf "spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions" \
  --conf "spark.sql.defaultCatalog=spark_catalog" \
  --conf "spark.sql.catalog.spark_catalog=org.apache.iceberg.spark.SparkCatalog" \
  --conf "spark.sql.catalog.spark_catalog.type=rest" \
  --conf "spark.sql.catalog.spark_catalog.uri=https://s3tables.us-east-1.amazonaws.com/iceberg" \
  --conf "spark.sql.catalog.spark_catalog.warehouse=arn:aws:s3tables:<region>:<account-id>:bucket/<table-bucket-name>" \
  --conf "spark.sql.catalog.spark_catalog.rest.sigv4-enabled=true" \
  --conf "spark.sql.catalog.spark_catalog.rest.signing-name=s3tables" \
  --conf "spark.sql.catalog.spark_catalog.rest.signing-region=<region>" \
  --conf "spark.sql.catalog.spark_catalog.io-impl=org.apache.iceberg.aws.s3.S3FileIO" \
  --conf "spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialProvider" \
  --conf "spark.sql.catalog.spark_catalog.rest-metrics-reporting-enabled=false" \
  --driver-memory 4G --executor-memory 8G \
  import_from_json.py ./json_data --database security_graph
```

## Deployment
- Start PuppyGraph using Docker by running the following command:
```bash
docker run -p 8081:8081 -p 8182:8182 -p 7687:7687 -e PUPPYGRAPH_PASSWORD=puppygraph123 -d --name puppy --rm --pull=always puppygraph/puppygraph:stable
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
- To stop and remove the Puppygraph container, run:
```bash
docker stop puppy
```
