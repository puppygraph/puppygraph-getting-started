# Ethereum Blockchain Graph Demo

## Summary
This demo shows how to query the [AWS Public Blockchain Dataset](https://registry.opendata.aws/aws-public-blockchain/) as a graph using PuppyGraph. In this demo, we start from a [known phishing wallet](https://etherscan.io/address/0xbe356f13b7b1bc6d89abcbd6272b40427231411f), trace USDT flows through intermediary addresses and surface hidden cycles connecting suspicious entities. The result is a zero-ETL graph query layer over live blockchain data.

## Prerequisites
- Docker
- AWS CLI
- An AWS account with permissions for S3 and Glue

## Note
The Data Preparation step below populates a date-scoped subset of Ethereum transaction data for demonstration purposes. For real-world use cases, you can directly connect your existing data sources to PuppyGraph without data preparation. You can either use publicly available sample data or apply your own datasets.

## Data Preparation

### 1. Configure AWS credentials
```bash
aws configure --profile your-profile
export AWS_PROFILE=your-profile
```

Copy `.env.example` to `.env` and fill in your values:
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
aws s3 mb s3://your-private-bucket
aws s3 mb s3://aws-web3-eth-demo
```

To adjust the date range of the data, edit `config.py`:
```python
DATE_START = "2026-01-01"
DATE_END   = "2026-01-01"
```

Then fetch the data:
```bash
uv run get_data.py --profile your-profile
```

### 4. Run the connectivity check
Verifies your credentials, bucket access, and Glue reachability before running anything that writes metadata.
```bash
uv run check_aws_connectivity.py --profile your-profile
```

### 5. Register the Iceberg table
Spin up the official Spark container and run `setup.py` via `spark-submit`. This creates an empty Iceberg table in Glue and registers the Parquet files for your configured date range — no data is moved.
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
- `--delete-partitions START END` — Cleanly removes partitions from Iceberg and S3 for the given date range, e.g. `--delete-partitions 2026-01-02 2026-01-07`.

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

2. Upload the schema `schema.json` after replacing the credential placeholders (`access-key`, `secret-key`, and `region`) with your actual values:
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

1. Find All Wallets Feeding a Suspicious Address
   ```cypher
   MATCH path = (funder:Address)-[:TRANSFERS_TOKEN_TO*2..3]->(x:Address)
   WHERE id(x) = 'Address[0x000000000000000000000000bdf9c0abe5b265671ad4efc365f6c0ad05d4fe89]'
     AND ALL(e IN relationships(path)
         WHERE e.token_address = '0xdac17f958d2ee523a2206206994597c13d831ec7')
   RETURN path
   LIMIT 300
   ```
  ![](/use-case-demos/web3-eth-aws-demo/images/1.png)

2. Trace USDT Flows Leaving a Suspicious Wallet
   ```cypher
   MATCH path = (x:Address)-[:TRANSFERS_TOKEN_TO*2..3]->(dest:Address)
   WHERE id(x) = 'Address[0x000000000000000000000000bdf9c0abe5b265671ad4efc365f6c0ad05d4fe89]'
     AND ALL(e IN relationships(path)
         WHERE e.token_address = '0xdac17f958d2ee523a2206206994597c13d831ec7')
   RETURN path
   LIMIT 50
   ```
   ![](/use-case-demos/web3-eth-aws-demo/images/2.png)

3. Detect Hidden Cycles Through a Known Intermediary
   ```cypher
   MATCH path = (x:Address)-[:TRANSFERS_TOKEN_TO*4..6]->(x)
   WHERE id(x) = 'Address[0x000000000000000000000000bdf9c0abe5b265671ad4efc365f6c0ad05d4fe89]'
     AND ALL(e IN relationships(path)
         WHERE e.token_address = '0xdac17f958d2ee523a2206206994597c13d831ec7')
     AND ANY(n IN nodes(path)
         WHERE id(n) = 'Address[0x000000000000000000000000c266110eaae9bdfb2111e7b97e8303c4bc327420]')
   RETURN path
   LIMIT 10
   ```
  ![](/use-case-demos/web3-eth-aws-demo/images/3.png)

4. Surface Round-Trip Paths Through the Poisoning Wallet
   ```cypher
   MATCH path = (x:Address)-[:TRANSFERS_TOKEN_TO*2..3]->(poison:Address)-[:TRANSFERS_TOKEN_TO*2..3]->(x)
   WHERE id(x) = 'Address[0x000000000000000000000000bdf9c0abe5b265671ad4efc365f6c0ad05d4fe89]'
     AND id(poison) = 'Address[0x000000000000000000000000c266110eaae9bdfb2111e7b97e8303c4bc327420]'
     AND ALL(e IN relationships(path)
         WHERE e.token_address = '0xdac17f958d2ee523a2206206994597c13d831ec7')
   RETURN path
   LIMIT 10
   ```
   ![](/use-case-demos/web3-eth-aws-demo/images/4.png)

## Cleanup and Teardown
To stop and remove the PuppyGraph container, run:
```bash
docker stop puppy
```

To remove the Iceberg data and Glue database created for this demo, run:
```bash
aws s3 rm s3://your-private-bucket/iceberg/ --recursive
aws s3 rm s3://your-private-bucket/eth/ --recursive
aws glue delete-database --name eth_iceberg
```