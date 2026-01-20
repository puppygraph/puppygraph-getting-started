#  Cloud Security Graph Demo

## Summary
This demo shows how to build a SIEM-like investigation graph directly on Amazon S3 Tables using PuppyGraph. We use a public dataset of anonymized AWS CloudTrail logs from [flaws.cloud](https://summitroute.com/blog/2020/10/09/public_dataset_of_cloudtrail_logs_from_flaws_cloud/), a security training environment created by Scott Piper. It contains 1.9 million events simulating realistic attack scenarios in AWS—ideal for modeling real-world threat investigations.

## Prerequisites:
- Docker
- AWS CLI

## Note:
The Demo Data Preparation step below populates some example data for demonstration purposes. 
For real-world use cases, you can directly connect your existing data sources to PuppyGraph without the need for data preparation. 
In other words, you can either download and use publicly available sample data or apply your own real-world datasets.

## Data Preparation

1. Create a Table Bucket and a Namespace
   
   - Create a table bucket
     ```bash
     aws s3tables create-table-bucket \
         --region <region> \
         --name security-demo
     ```

   - Create a namespace
     ```bash
     aws s3tables create-namespace \
        --region <region> \
        --table-bucket-arn <table-bucket-arn> \
        --namespace security_graph
     ```

2. Stage the CloudTrail logs dataset and import script
   
   - Create a directory to host files and navigate into it
     ```bash
     mkdir -p ./spark-container
     cd ./spark-container
     ```

   - Download and Extract the Log Files
     ```bash
     wget https://summitroute.com/downloads/flaws_cloudtrail_logs.tar
     mkdir -p ./json_data
     tar -xvf flaws_cloudtrail_logs.tar --strip-components=1 -C ./json_data
     gunzip ./json_data/*.json.gz
     ```

   - Copy the import script and navigate back
     ```bash
     cp ../import_from_json.py .
     cd ..
     ```

3. Import the dataset to S3 Tables with a Docker container running Spark
   - Create a `.env` file in the `spark-container` directory with your AWS credentials and region:
     ```
     AWS_ACCESS_KEY_ID=<your-access-key>
     AWS_SECRET_ACCESS_KEY=<your-secret-key>
     AWS_REGION=<region>
     ```
   
   - Use a Docker container with Apache Spark to import the data. Replace `<your-access-key>`, `<your-secret-key>`, and `<region>` with your actual AWS credentials and region.
     ```bash
     # Run the official Spark docker container and open an interactive shell
     docker run -it \
       --name spark-container \
       -p 4040:4040 \
       -v ./spark-container:/spark-container \
       -w /spark-container \
       --env-file .env \
       --user root \
       apache/spark:3.5.1 \
       /bin/bash
     ```

   - In the interactive shell, set up the Spark PATH and install the necessary Python packages in your container.
     ```bash
     # Add Spark to PATH
     export PATH=$PATH:/opt/spark/bin
     
     # Install Python packages
     pip install --target=/spark-container/python_libs ijson faker
     export PYTHONPATH=/spark-container/python_libs:$PYTHONPATH
     ```
    
   - Submit a Spark job that imports the CloudTrail logs dataset and inserts the data into S3 Tables. Remember to replace `<region>`, and `<table-bucket-arn>` with your actual AWS region, account ID, and the table bucket ARN you created in step 1.
     ```bash
     # Run spark-submit
     spark-submit \
      --conf "spark.jars.ivy=/spark-container/ivy" \
      --master "local[*]" \
      --packages "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.1,software.amazon.awssdk:bundle:2.20.160,software.amazon.awssdk:url-connection-client:2.20.160" \
      --conf "spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions" \
      --conf "spark.sql.defaultCatalog=spark_catalog" \
      --conf "spark.sql.catalog.spark_catalog=org.apache.iceberg.spark.SparkCatalog" \
      --conf "spark.sql.catalog.spark_catalog.type=rest" \
      --conf "spark.sql.catalog.spark_catalog.uri=https://s3tables.<region>.amazonaws.com/iceberg" \
      --conf "spark.sql.catalog.spark_catalog.warehouse=<table-bucket-arn>" \
      --conf "spark.sql.catalog.spark_catalog.rest.sigv4-enabled=true" \
      --conf "spark.sql.catalog.spark_catalog.rest.signing-name=s3tables" \
      --conf "spark.sql.catalog.spark_catalog.rest.signing-region=<region>" \
      --conf "spark.sql.catalog.spark_catalog.io-impl=org.apache.iceberg.aws.s3.S3FileIO" \
      --conf "spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialProvider" \
      --conf "spark.sql.catalog.spark_catalog.rest-metrics-reporting-enabled=false" \
      --driver-memory 8G \
      import_from_json.py /spark-container/json_data --database security_graph
     ```
      
     Type `exit` to exit the container shell.

     After importing the data, you should see six tables in the table bucket under the namespace `security_graph` as we created in step 1.

4. Stop and remove the Spark container and clean up temporary files
   ```bash
   docker stop spark-container
   docker rm spark-container
   rm -r ./spark-container  
   rm .env
   ```

## PuppyGraph Deployment
Start PuppyGraph using Docker by running the following command:
  ```bash
  docker run \
  -p 8081:8081 -p 8182:8182 -p 7687:7687 \
  -e PUPPYGRAPH_PASSWORD=puppygraph123  -e QUERY_TIMEOUT=5m \
  -d --name puppy --rm --pull=always \
  puppygraph/puppygraph:stable
  ```

## Modeling the Graph

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
   - Username: `puppygraph`
   - Password: `puppygraph123`

2. Upload the schema `schema.json` after replacing the placeholders (`access-key`, `secret-key`, `table-bucket-arn`, and `region`) in the catalog with your actual AWS credentials, table bucket ARN, and region:
   - Select the file `schema.json` in the Upload Graph Schema JSON section and click on Upload.
   - You can also use `curl` command to upload the schema in the terminal:
     ```bash
     curl -XPOST -H "content-type: application/json" \
     --data-binary @./schema.json \
     --user "puppygraph:puppygraph123" \
     localhost:8081/schema
     ```

## Querying the Graph

- Navigate to the Query panel on the left side. The Graph Query tab offers an interactive environment for querying the graph using Gremlin and Cypher.
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. You can do this by clicking the "Clear Canvas" button located in the top-right corner of the page.

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

- To remove the S3 Tables created for this demo, run the cleanup_s3tables.sh script interactively: 
  ```bash
  chmod +x cleanup_s3tables.sh
  ./cleanup_s3tables.sh --region <region> --table-bucket-arn <table-bucket-arn> --namespace security_graph
  ```


