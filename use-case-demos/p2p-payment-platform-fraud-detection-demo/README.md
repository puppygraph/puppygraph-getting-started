#  P2P Payment Platform Fraud Detection Demo

## Prerequisites:
- Docker
- Docker Compose
- Python 3


## Summary

This P2P Payment Platform Fraud Detection Demo investigates real anonymized data from a peer-to-peer (P2P) payment platform to identify fraud patterns, resolve high-risk fraud communities, and apply recommendation methods.  
Through the use of graph analysis, we uncover new fraud risks that went undetected by non-graph methods, increasing the number of flagged users by 87.5%.  
By leveraging a graph schema that includes connections between credit cards, devices, and IP addresses, the system can analyze these relationships to reveal hidden fraud networks.  
Each user node contains an indicator variable (MoneyTransferFraud) set to 1 for known fraud, determined by credit card chargeback events and manual review, or 0 otherwise.  
This knowledge graph enables the detection of fraudulent activities on a larger scale, significantly enhancing fraud mitigation strategies.

- **`README.md`**: Provides an overview of the project, including setup instructions and key details about the fraud detection process.
- **`docker-compose.yaml`**: Sets up the necessary services using Docker, defining containers and environments such as databases and applications to run the demo.
- **`wcc_fraud_detection.py`**: Implements the WCC algorithm to identify suspected fraudulent users based on their connections to known fraudsters.
- **`parquet_data/`**:  Contains Parquet files generated from CSV files, used for importing data into Iceberg for further analysis. This dataset was provided by [p2p-dataset](https://drive.google.com/drive/folders/1LaNFObKnZb1Ty8T7kPLCYlXDUlHU7FGa). It is licensed under the Open Data Commons Attribution License (ODC-BY). Modifications have been made to the original dataset. You can find the license details [here](https://opendatacommons.org/licenses/by/).

## Deployment
- Run the following command to start the Apache Iceberg services and PuppyGraph:
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

## Data Preparation
- Start the Spark-SQL shell to access Iceberg by running:
```bash
sudo docker exec -it spark-iceberg spark-sql
```
The shell prompt will appear as:
```shell
spark-sql ()>
```

- Execute the following SQL statements in the shell to create tables and import data:
```sql
CREATE DATABASE fraud_db;

CREATE EXTERNAL TABLE fraud_db.Card (
  id BIGINT,
  cardType STRING,
  level STRING,
  guid STRING
) USING iceberg;

CREATE EXTERNAL TABLE fraud_db.Device (
  id BIGINT,
  os STRING,
  device STRING,
  guid STRING
) USING iceberg;

CREATE EXTERNAL TABLE fraud_db.IP (
  id BIGINT,
  guid STRING
) USING iceberg;

CREATE EXTERNAL TABLE fraud_db.User (
  id BIGINT,
  fraudMoneyTransfer INT,
  firstChargebackMtDate DATE,
  moneyTransferErrorCancelAmount FLOAT,
  guid STRING
) USING iceberg;

CREATE EXTERNAL TABLE fraud_db.HAS_CC (
  id BIGINT,
  from_user_id BIGINT,
  to_card_id BIGINT,
  cardDate DATE
) USING iceberg;

CREATE EXTERNAL TABLE fraud_db.HAS_IP (
  id BIGINT,
  from_user_id BIGINT,
  to_ip_id BIGINT,
  ipDate DATE
) USING iceberg;

CREATE EXTERNAL TABLE fraud_db.P2P (
  id BIGINT,
  from_user_id BIGINT,
  to_user_id BIGINT,
  transactionDateTime TIMESTAMP,
  totalAmount FLOAT
) USING iceberg;

CREATE EXTERNAL TABLE fraud_db.REFERRED (
  id BIGINT,
  from_user_id BIGINT,
  to_user_id BIGINT
) USING iceberg;

CREATE EXTERNAL TABLE fraud_db.USED (
  id BIGINT,
  from_user_id BIGINT,
  to_device_id BIGINT,
  deviceDate DATE
) USING iceberg;

INSERT INTO fraud_db.Card 
SELECT * FROM parquet.`/parquet_data/Card.parquet`;

INSERT INTO fraud_db.Device 
SELECT * FROM parquet.`/parquet_data/Device.parquet`;

INSERT INTO fraud_db.IP 
SELECT * FROM parquet.`/parquet_data/IP.parquet`;

INSERT INTO fraud_db.User 
SELECT id, 
       fraudMoneyTransfer, 
       CAST(firstChargebackMtDate AS DATE), 
       moneyTransferErrorCancelAmount, 
       guid 
FROM parquet.`/parquet_data/User.parquet`;

INSERT INTO fraud_db.HAS_CC 
SELECT id, 
       from_user_id,
       to_card_id, 
       CAST(cardDate AS DATE)
FROM parquet.`/parquet_data/HAS_CC.parquet`;

INSERT INTO fraud_db.HAS_IP 
SELECT id, 
       from_user_id,
       to_ip_id, 
       CAST(ipDate AS DATE)
FROM parquet.`/parquet_data/HAS_IP.parquet`;

INSERT INTO fraud_db.P2P 
SELECT id, 
       from_user_id,
       to_user_id, 
       CAST(transactionDateTime AS TIMESTAMP),
       totalAmount
FROM parquet.`/parquet_data/P2P.parquet`;

INSERT INTO fraud_db.REFERRED 
SELECT id, 
       from_user_id,
       to_user_id
FROM parquet.`/parquet_data/REFERRED.parquet`;

INSERT INTO fraud_db.USED 
SELECT id, 
       from_user_id,
       to_device_id, 
       CAST(deviceDate AS DATE)
FROM parquet.`/parquet_data/USED.parquet`;

CREATE TABLE IF NOT EXISTS fraud_db.SharedCardTransfers (
    id BIGINT,
    from_user_id BIGINT,
    to_user_id BIGINT
) USING iceberg;

INSERT INTO fraud_db.SharedCardTransfers (id, from_user_id, to_user_id)
SELECT
    ROW_NUMBER() OVER (ORDER BY from_user_id) AS id,
    from_user_id,
    to_user_id
FROM (
    SELECT 
        DISTINCT p.from_user_id,
        p.to_user_id
    FROM 
        fraud_db.P2P p
    JOIN 
        fraud_db.HAS_CC c1 ON p.from_user_id = c1.from_user_id
    JOIN 
        fraud_db.HAS_CC c2 ON p.to_user_id = c2.from_user_id
    WHERE 
        c1.to_card_id = c2.to_card_id
) t;

```
- Exit the Spark-SQL shell:
```sql
quit;
```

## Modeling the Graph
- Log into PuppyGraph Web UI at http://localhost:8081 with username `puppygraph` and password `puppygraph123`.
- Upload the schema by selecting the file `schema.json` in the Upload Graph Schema JSON block and clicking on Upload.


## Querying the Graph by Web

- Click on the Query panel on the left side. The Cypher Console tab offers an interactive environment for querying the graph using Cypher.

1. Query confirmed financial fraud users
```cypher
MATCH (u:User) WHERE u.fraudMoneyTransfer = 1 RETURN u
```

2. Group accounts with transfer records and shared credit cards using the WCC algorithm
```cypher
CALL algo.wcc({labels: ['User'],relationshipTypes: ['PatternAssociation']}) YIELD id, componentId RETURN componentId, collect(id) as ids order by size(ids) desc
```

## Querying the Graph by Code
- Use the script wcc_fraud_detection.py to connect to PuppyGraph and identify suspected fraudulent users through the WCC algorithm:
```bash
python3 wcc_fraud_detection.py
```

## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
sudo docker compose down --volumes --remove-orphans
```
