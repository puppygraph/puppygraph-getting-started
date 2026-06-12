# Ethereum Blockchain Graph Demo

## Summary
This demo shows how to query the [AWS Public Blockchain Dataset](https://registry.opendata.aws/aws-public-blockchain/) as a graph using PuppyGraph. Starting from a [known phishing wallet](https://etherscan.io/address/0xbe356f13b7b1bc6d89abcbd6272b40427231411f) flagged by HashDit, we trace ETH gas-funding infrastructure and USDT flows through a coordinated collection network to its final destinations. Zero ETL required.

AWS Public Blockchain Data was accessed on 2026-05-20 from https://registry.opendata.aws/aws-public-blockchain.

## Prerequisites
- Docker
- AWS CLI
- An AWS account with permissions for S3 and Glue

## Data Preparation

### 1. Configure AWS credentials
```bash
aws configure --profile demo
export AWS_PROFILE=demo
```

Copy `.env.example` to `.env` and fill in your your AWS credentials and region:
```bash
cp .env.example .env
```

AWS CLI credentials are for the setup scripts; .env credentials are for the Docker containers, which don't inherit your shell environment.

### 2. Install dependencies
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Create a private S3 bucket for Parquet data

```bash
aws s3 mb s3://aws-web3-eth-demo --profile demo
```

The following can be configured via environment variables (or exported before running):

```bash
export TARGET_BUCKET="aws-web3-eth-demo" # Bucket for s3 data and metadata
export TARGET_DB="eth_iceberg" # Glue database name
export AWS_REGION="us-east-1"
export DATE_START="2026-01-01"
export DATE_END="2026-01-01"
```

Then fetch the data:
```bash
uv run get_data.py --profile demo
```

### 4. Run the connectivity check
Verifies your credentials, bucket access, and Glue reachability before running anything that writes metadata.
```bash
uv run check_aws_connectivity.py --profile demo
```

### 5. Register the Iceberg table
Spin up the official Spark container and run `setup.py` via `spark-submit`. This creates an empty Iceberg table in Glue and registers all Parquet files currently present under `s3://$TARGET_BUCKET/eth/<table>/` — no data is moved. If your bucket already contains multiple date partitions, make sure it only includes the partitions you want to register before running this step.
```bash
docker run -it \
  --name spark-container \
  -p 4040:4040 \
  -v .:/spark-container \
  -w /spark-container \
  --env-file .env \
  --user root \
  apache/spark:3.5.1 \
  /bin/bash
```

Inside the container:
```bash
export PATH=$PATH:/opt/spark/bin

spark-submit \
  --packages "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.9.2,org.apache.iceberg:iceberg-aws-bundle:1.9.2,org.apache.hadoop:hadoop-aws:3.3.4" \
  --conf "spark.jars.ivy=/spark-container/ivy" \
  setup.py --create --add-files
```

The setup script supports the following flags:

- `--create` — Creates the Iceberg tables in Glue if they don't already exist.
- `--add-files` — Registers the Parquet files for the configured date range as Iceberg metadata. No data is moved.
- `--create --add-files` — Run together for a fresh setup.

Type `exit` when done, then clean up the container:
```bash
docker stop spark-container
docker rm spark-container
```

## PuppyGraph Deployment
Start PuppyGraph using Docker by running the following command:
```bash
docker run \
  -p 8081:8081 -p 8182:8182 -p 7687:7687 \
  --env-file .env \
  -e PUPPYGRAPH_PASSWORD=puppygraph123 \
  -d --name puppy --rm --pull=always \
  puppygraph/puppygraph:1.0-preview
```

## Modeling the Graph

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
   - Username: `puppygraph`
   - Password: `puppygraph123`

2. Upload the schema `schema.json`:
   - Select `schema.json` in the Upload Graph Schema JSON section and click **Upload**.
   - You can also use `curl` to upload the schema from the terminal:
     ```bash
     curl -XPOST -H "content-type: application/json" \
       --data-binary @./schema.json \
       --user "puppygraph:puppygraph123" \
       localhost:8081/schema
     ```

## Querying the Graph

Navigate to the Query panel on the left side. The Graph Query tab offers an interactive environment for querying the graph using Gremlin and Cypher. After each query, remember to clear the graph panel before executing the next query. You can do this by clicking the **Clear Canvas** button in the top-right corner.

Example Queries:

1. Who is the controller funding, and at what scale?
```cypher
MATCH path = (controller:Address)-[:TRANSACTS_TO*2..3]->(wallet:Address)
WHERE id(controller) = 'Address[0xbe356f13b7b1bc6d89abcbd6272b40427231411f]'
RETURN path, id(wallet)
LIMIT 100
```
![](/use-case-demos/web3-eth-aws-demo/images/1.png)

2. Which wallets are feeding the collection address?
```cypher
MATCH path = (src:Address)-[:TRANSFERS_TOKEN_TO*1..3]->(x:Address)
WHERE id(x) = 'Address[0x00000000000000000000000006fd7938a3bfe3be6eee4c8626048d7489f793b0]'
  AND ALL(e IN relationships(path)
      WHERE e.token_address = '0xdac17f958d2ee523a2206206994597c13d831ec7')
RETURN path
LIMIT 300
```
![](/use-case-demos/web3-eth-aws-demo/images/2.png)

3. Where does the USDT flow after leaving the collection point?
```cypher
MATCH path = (x:Address)-[:TRANSFERS_TOKEN_TO*1..3]->(dst:Address)
WHERE id(x) = 'Address[0x00000000000000000000000006fd7938a3bfe3be6eee4c8626048d7489f793b0]'
  AND ALL(e IN relationships(path)
      WHERE e.token_address = '0xdac17f958d2ee523a2206206994597c13d831ec7')
RETURN path
LIMIT 300
```
![](/use-case-demos/web3-eth-aws-demo/images/3.png)

## Cleanup and Teardown
To stop and remove the PuppyGraph container, run:
```bash
docker stop puppy
```

To remove the Iceberg data and Glue database created for this demo, run:
```bash
# Replace aws-web3-eth-demo and eth_iceberg if you changed the defaults
aws s3 rm s3://aws-web3-eth-demo/iceberg/ --recursive --profile demo
aws s3 rm s3://aws-web3-eth-demo/eth/ --recursive --profile demo
aws glue delete-database --name eth_iceberg --profile demo
```