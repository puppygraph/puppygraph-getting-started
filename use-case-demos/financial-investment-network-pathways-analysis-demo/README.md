#  Financial Investment Network Pathways Analysis Demo

## Summary
This demo showcases how financial services can unravel the web of connections from investment groups to individual securities, traversing through entities like persons, trusts, and accounts.  
Financial firms can utilize this to visualize investment pathways, assess group and individual asset balances, and identify key security holders, enabling a deeper understanding of investment structures and the distribution of assets within intricate financial portfolios for their clients.

- **`README.md`**: Provides an overview of the project, including setup instructions and key details about the demo.
- **`docker-compose.yaml`**: Sets up the necessary services using Docker, defining containers and environments such as databases and applications for running the demo.
- **`CsvToParquet.py`**: Converts CSV files into Parquet format for easier data import into Iceberg.
- **`csv_data/`**:  Contains randomly generated CSV files representing various entities in the financial investment network, such as groups, persons, trusts, accounts, and securities. These files are used as input for conversion to Parquet format before being imported into Iceberg.

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
CREATE DATABASE Financial_Service;

CREATE EXTERNAL TABLE Financial_Service.Group (
  ID    BIGINT,
  Name  STRING
) USING iceberg;

CREATE EXTERNAL TABLE Financial_Service.Person (
  ID        BIGINT,
  Name      STRING,
  Birthday  DATE,
  Email     STRING,
  PhoneNum  STRING
) USING iceberg;

CREATE EXTERNAL TABLE Financial_Service.Trust (
  ID        BIGINT,
  Name      STRING,
  TrustType STRING
) USING iceberg;

CREATE EXTERNAL TABLE Financial_Service.Account (
  ID            BIGINT,
  AccountNumber STRING,
  AccountType   STRING,
  Balance       DOUBLE
) USING iceberg;

CREATE EXTERNAL TABLE Financial_Service.Securities (
  ID            BIGINT,
  SecurityType  STRING,
  SecurityName  STRING,
  CurrentPrice  FLOAT
) USING iceberg;

CREATE EXTERNAL TABLE Financial_Service.AccountSecurities (
  ID            BIGINT,
  AccountID     BIGINT,
  SecurityID    BIGINT,
  Quantity      INT,
  PurchaseDate  DATE,
  PurchasePrice FLOAT
) USING iceberg;

CREATE EXTERNAL TABLE Financial_Service.GroupPerson (
  ID        BIGINT,
  GroupID   BIGINT,
  PersonID  BIGINT
) USING iceberg;

CREATE EXTERNAL TABLE Financial_Service.PersonTrust (
  ID        BIGINT,
  PersonID  BIGINT,
  TrustID   BIGINT,
  Weight    FLOAT
) USING iceberg;

CREATE EXTERNAL TABLE Financial_Service.TrustAccount (
  ID        BIGINT,
  TrustID   BIGINT,
  AccountID BIGINT
) USING iceberg;

INSERT INTO Financial_Service.Group 
SELECT * FROM parquet.`/parquet_data/Group.parquet`;

INSERT INTO Financial_Service.Person 
SELECT ID,
       Name, 
       CAST(Birthday AS DATE), 
       Email, 
       PhoneNum 
FROM parquet.`/parquet_data/Person.parquet`;

INSERT INTO Financial_Service.Trust 
SELECT * FROM parquet.`/parquet_data/Trust.parquet`;

INSERT INTO Financial_Service.Account 
SELECT * FROM parquet.`/parquet_data/Account.parquet`;

INSERT INTO Financial_Service.Securities 
SELECT * FROM parquet.`/parquet_data/Securities.parquet`;

INSERT INTO Financial_Service.AccountSecurities 
SELECT ID,
       AccountID, 
       SecurityID,
       Quantity,
       CAST(PurchaseDate AS DATE), 
       PurchasePrice 
FROM parquet.`/parquet_data/AccountSecurities.parquet`;

INSERT INTO Financial_Service.GroupPerson 
SELECT * FROM parquet.`/parquet_data/GroupPerson.parquet`;

INSERT INTO Financial_Service.PersonTrust 
SELECT * FROM parquet.`/parquet_data/PersonTrust.parquet`;

INSERT INTO Financial_Service.TrustAccount 
SELECT * FROM parquet.`/parquet_data/TrustAccount.parquet`;

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

## Querying the Graph using Gremlin

- Navigate to the Query panel on the left side. The **Graph Query** tab offers an interactive environment for querying the graph using Gremlin and openCypher.

Example Queries:
1. Count the number of unique paths from "Group" to "Securities" by traversing through "Person", "Trust", "Account"
```gremlin
g.V().hasLabel('Group')
  .out('GroupHasPerson')
  .out('PersonHasTrust')
  .out('TrustHasAccount')
  .out('AccountHasSecurities')
  .path()
  .count()
```

2. Visualize all paths from a specific "Group" to "Securities".
```gremlin
g.V().hasLabel('Group').has('Name', 'Warren Group')
  .out('GroupHasPerson')
  .out('PersonHasTrust')
  .out('TrustHasAccount')
  .out('AccountHasSecurities')
  .path()
```

3. Query the top 10 groups with the highest total account balances
```gremlin
g.V().hasLabel('Group')
  .group()
    .by(id)
    .by(
      __.out('GroupHasPerson')
        .out('PersonHasTrust')
        .out('TrustHasAccount')
        .values('Balance')
        .sum()
    )
  .order(local)
    .by(values, desc)
  .limit(local, 10)
```

4. Query the top 10 persons who hold the most of the specified security, considering the weight factor.
```cypher
MATCH (s:Securities {SecurityName: 'Webster-Crawford'})<-[as:AccountHasSecurities]-(a:Account)<-[:TrustHasAccount]-(t:Trust)<-[pt:PersonHasTrust]->(p:Person) WITH p, as.Quantity * pt.Weight AS weightedQuantity RETURN p.Name, sum(weightedQuantity) AS totalWeightedQuantity ORDER BY totalWeightedQuantity DESC LIMIT 10
```

## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
sudo docker compose down --volumes --remove-orphans
```
