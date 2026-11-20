# Integrating AWS S3 Tables and Querying Data Using PuppyGraph

For a more complex S3 Tables demo, please refer to the [CloudTrail S3 Tables demo](../../use-case-demos/cloudtrail-s3tables-demo/).

## Summary
This demo showcases a graph analysis workflow by integrating aws S3 tables with PuppyGraph. 
We create s3 tables in aws s3 table buckets, then query it using PuppyGraph’s graph database interface. 
This process streamlines storage, data processing and visualization, enabling graph insights from relational data.

## Prerequisites

- [An aws account](https://aws.amazon.com/)
- [aws cli version 2](https://aws.amazon.com/cli/)
- [Docker](https://www.docker.com/)

## Before we start
It is strongly recommended to take the getting-started tutorial of AWS [S3 Tables](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-getting-started.html) first to become familiar with AWS S3 Tables and resolve IAM problems. In this demo, we will use a similar approach when creating tables.

## Data preparation

### Create table bucket 
Follow the getting-started tutorial of s3 tables to create a table bucket.

### Create namespace
Use aws cli to create a namespace. Replace the placeholders with your real value.
```bash
aws s3tables create-namespace \
    --table-bucket-arn <table-bucket-arn> \
    --namespace puppygraph_test
```

### Create tables
Use aws cli to create tables. Replace the placeholders in corresponded files by your real value.
```bash
aws s3tables create-table --cli-input-json file://table_definition/person_definition.json
aws s3tables create-table --cli-input-json file://table_definition/software_definition.json
aws s3tables create-table --cli-input-json file://table_definition/knows_definition.json
aws s3tables create-table --cli-input-json file://table_definition/created_definition.json
```

### Integrate the table bucket with AWS analytics services
Athena reads S3 Tables through the AWS Glue Data Catalog. Create the table bucket with **Enable integration** selected, or follow [Integrating Amazon S3 Tables with AWS analytics services](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-integrating-aws.html).

### Insert data
Use AWS [Athena](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-integrating-athena.html) to insert data into tables.
```sql
INSERT INTO person VALUES
('v1', 'marko', 29),
('v2', 'vadas', 27),
('v4', 'josh', 32),
('v6', 'peter', 35);

INSERT INTO software VALUES
('v3', 'lop', 'java'),
('v5', 'ripple', 'java');

INSERT INTO created VALUES
('e9', 'v1', 'v3', 0.4),
('e10', 'v4', 'v5', 1.0),
('e11', 'v4', 'v3', 0.4),
('e12', 'v6', 'v3', 0.2);

INSERT INTO knows VALUES
('e7', 'v1', 'v2', 0.5),
('e8', 'v1', 'v4', 1.0);
```

## Connecting to PuppyGraph

### Start PuppyGraph
```bash
docker run \
  -p 8081:8081 -p 8182:8182 -p 7687:7687 \
  -e PUPPYGRAPH_PASSWORD=puppygraph123  -e QUERY_TIMEOUT=5m \
  -d --name puppy --rm --pull=always \
  puppygraph/puppygraph:latest
```

### Log into the UI
Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
    - Username: `puppygraph`
    - Password: `puppygraph123`

### Modeling the Graph
Upload the schema:
- Replace the placeholder in `schema.json` by your real value. (`table-bucket-arn` is something like `arn:aws:s3tables:<region>:<account-id>:bucket/<table-bucket-name>`.)
- Click **Upload Schema**, select the file `schema.json` and click **Upload**.

## Querying via PuppyGraph

Navigate to **Query** in the Web UI:

- Use **Graph Query** for Gremlin/openCypher queries with visualization.

### Example Queries

- Retrieve an vertex named 'marko'.

    Gremlin:
    ```gremlin
    g.V().has("name", "marko").valueMap()
    ```
    openCypher:
    ```cypher
    MATCH (v {name: 'marko'}) RETURN v
    ```

- Retrieve the paths from "marko" to the software created by those whom "marko" knows.
    Gremlin:
    ```gremlin
    g.V().has("name", "marko")
    .out("knows").out("created").path()
    ```
    openCypher:
    ```cypher
    MATCH p=(v {name: 'marko'})-[:knows]->()-[:created]->()
    RETURN p
    ```

### Teardown
- Stop the PuppyGraph container.
  ```bash
  docker stop puppy
  ```
- To delete the created tables, namespace, and bucket, use the aws cli commands:
  ```bash
  # Delete the tables
  aws s3tables delete-table \
      --region <region> \
      --table-bucket-arn <table-bucket-arn> \
      --namespace puppygraph_test  \
      --name person 

  aws s3tables delete-table \
      --region <region> \
      --table-bucket-arn <table-bucket-arn> \
      --namespace puppygraph_test  \
      --name software

  aws s3tables delete-table \
      --region <region> \
      --table-bucket-arn <table-bucket-arn> \
      --namespace puppygraph_test  \
      --name knows
  
  aws s3tables delete-table \
      --region <region> \
      --table-bucket-arn <table-bucket-arn> \
      --namespace puppygraph_test  \
      --name created

  # Delete the namespace
  aws s3tables delete-namespace \
      --region <region> \
      --table-bucket-arn <table-bucket-arn> \
      --namespace puppygraph_test
  
  # Delete the table bucket
  aws s3tables delete-table-bucket \
      --region <region> \
      --table-bucket-arn <table-bucket-arn>
  ```