# Integrating DeltaStream with Snowflake and Querying Data Using PuppyGraph

## Summary
This demo demonstrates the integration of DeltaStream with Snowflake by importing data from Kafka, followed by querying Snowflake data using PuppyGraph.  
The workflow enables users to process, store, and visualize data seamlessly with a graph database interface.

## Prerequisites

- Docker
- kafka
- Snowflake

## Setting up Kafka
1. Set kafka server config
```server.properties
listeners = PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://<AWS Public IPv4 DNS>:9092
broker.id=1
num.partitions=1
```
2. Start zookeeper and kafka server
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties &
bin/kafka-server-start.sh config/server.properties &
```

3. Create kafka topic
```bash
bin/kafka-topics.sh --create --topic kafka-Account --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-AccountRepayLoan --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-AccountTransferAccount --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-AccountWithdrawAccount --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-Company --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-CompanyApplyLoan --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-CompanyGuaranteeCompany --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-CompanyInvestCompany --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-CompanyOwnAccount --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-Loan --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-LoanDepositAccount --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-Medium --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-MediumSignInAccount --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-Person --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-PersonApplyLoan --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-PersonGuaranteePerson --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-PersonInvestCompany --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic kafka-PersonOwnAccount --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

## Deltastream Connect to Kafka
1. Log in to the Deltastream console and navigate to Resources.
2. Add a Kafka Store with the following settings:

| Parameter                       | Value                                                                        |
|---------------------------------|------------------------------------------------------------------------------|
| STORE TYPE                      | kafka.                                                                       |
| Name                            | store name; for example: `kafka_demo`.                                       |
| Region                          | Specifies the region of the Store; for axample: `AWS us-east-1`              |
| Add One Or More Urls To Connect | Hostname:port; for example: `ec2-1-111-111-111.compute-1.amazonaws.com:9092` |
| Disable SSL Encryption          | Specifies if the store should be accessed over TLS.                          |
| SASL Hash Function              | SASL hash function to use when authenticating with Apache Kafka brokers.     |

3. In the Workspace, create a deltastream catalog, for example: `kafka_db`
4. Create streams for Kafka topics via Deltastream SQL
```
-- 1. Account
CREATE STREAM account_stream (
  "label" STRING,
  "accountId" BIGINT,
  "createTime" STRING,
  "isBlocked" BOOLEAN,
  "accoutType" STRING,
  "nickname" STRING,
  "phonenum" STRING,
  "email" STRING,
  "freqLoginType" STRING,
  "lastLoginTime" STRING,
  "accountLevel" STRING
) WITH (
  'topic' = 'kafka-Account',
  'value.format' = 'JSON'
);

-- 2. AccountRepayLoan
CREATE STREAM accountrepayloan_stream (
  "label" STRING,
  "accountrepayloanId" BIGINT,
  "accountId" BIGINT,
  "loanId" BIGINT,
  "amount" DOUBLE,
  "createTime" STRING
) WITH (
  'topic' = 'kafka-AccountRepayLoan',
  'value.format' = 'JSON'
);

-- 3. AccountTransferAccount
CREATE STREAM accounttransferaccount_stream (
  "label" STRING,
  "accounttransferaccountId" BIGINT,
  "fromId" BIGINT,
  "toId" BIGINT,
  "amount" DOUBLE,
  "createTime" STRING,
  "orderNum" BIGINT,
  "comment" STRING,
  "payType" STRING,
  "goodsType" STRING
) WITH (
  'topic' = 'kafka-AccountTransferAccount',
  'value.format' = 'JSON'
);

-- 4. AccountWithdrawAccount
CREATE STREAM accountwithdrawaccount_stream (
  "label" STRING,
  "accountwithdrawaccountId" BIGINT,
  "fromId" BIGINT,
  "toId" BIGINT,
  "amount" DOUBLE,
  "createTime" STRING
) WITH (
  'topic' = 'kafka-AccountWithdrawAccount',
  'value.format' = 'JSON'
);

-- 5. Company
CREATE STREAM company_stream (
  "label" STRING,
  "companyId" BIGINT,
  "companyName" STRING,
  "isBlocked" BOOLEAN,
  "createTime" STRING,
  "country" STRING,
  "city" STRING,
  "business" STRING,
  "description" STRING,
  "url" STRING
) WITH (
  'topic' = 'kafka-Company',
  'value.format' = 'JSON'
);

-- 6. CompanyApplyLoan
CREATE STREAM companyapplyloan_stream (
  "label" STRING,
  "companyapplyloanId" BIGINT,
  "companyId" BIGINT,
  "loanId" BIGINT,
  "createTime" STRING,
  "org" STRING
) WITH (
  'topic' = 'kafka-CompanyApplyLoan',
  'value.format' = 'JSON'
);

-- 7. CompanyGuaranteeCompany
CREATE STREAM companyguaranteecompany_stream (
  "label" STRING,
  "companyguaranteecompanyId" BIGINT,
  "fromId" BIGINT,
  "toId" BIGINT,
  "createTime" STRING,
  "relation" STRING
) WITH (
  'topic' = 'kafka-CompanyGuaranteeCompany',
  'value.format' = 'JSON'
);

-- 8. CompanyInvestCompany
CREATE STREAM companyinvestcompany_stream (
  "label" STRING,
  "companyinvestcompanyId" BIGINT,
  "investorId" BIGINT,
  "companyId" BIGINT,
  "ratio" DOUBLE,
  "createTime" STRING
) WITH (
  'topic' = 'kafka-CompanyInvestCompany',
  'value.format' = 'JSON'
);

-- 9. CompanyOwnAccount
CREATE STREAM companyownaccount_stream (
  "label" STRING,
  "companyownaccountId" BIGINT,
  "companyId" BIGINT,
  "accountId" BIGINT,
  "createTime" STRING
) WITH (
  'topic' = 'kafka-CompanyOwnAccount',
  'value.format' = 'JSON'
);

-- 10. Loan
CREATE STREAM loan_stream (
  "label" STRING,
  "loanId" BIGINT,
  "loanAmount" DOUBLE,
  "balance" DOUBLE,
  "createTime" STRING,
  "loanUsage" STRING,
  "interestRate" DOUBLE
) WITH (
  'topic' = 'kafka-Loan',
  'value.format' = 'JSON'
);

-- 11. LoanDepositAccount
CREATE STREAM loandepositaccount_stream (
  "label" STRING,
  "loandepositaccountId" BIGINT,
  "loanId" BIGINT,
  "accountId" BIGINT,
  "amount" DOUBLE,
  "createTime" STRING
) WITH (
  'topic' = 'kafka-LoanDepositAccount',
  'value.format' = 'JSON'
);

-- 12. Medium
CREATE STREAM medium_stream (
  "label" STRING,
  "mediumId" BIGINT,
  "mediumType" STRING,
  "isBlocked" BOOLEAN,
  "createTime" STRING,
  "lastLoginTime" STRING,
  "riskLevel" STRING
) WITH (
  'topic' = 'kafka-Medium',
  'value.format' = 'JSON'
);

-- 13. MediumSignInAccount
CREATE STREAM mediumsigninaccount_stream (
  "label" STRING,
  "mediumsigninaccountId" BIGINT,
  "mediumId" BIGINT,
  "accountId" BIGINT,
  "createTime" STRING,
  "location" STRING
) WITH (
  'topic' = 'kafka-MediumSignInAccount',
  'value.format' = 'JSON'
);

-- 14. Person
CREATE STREAM person_stream (
  "label" STRING,
  "personId" BIGINT,
  "personName" STRING,
  "isBlocked" BOOLEAN,
  "createTime" STRING,
  "gender" STRING,
  "birthday" STRING,
  "country" STRING,
  "city" STRING
) WITH (
  'topic' = 'kafka-Person',
  'value.format' = 'JSON'
);

-- 15. PersonApplyLoan
CREATE STREAM personapplyloan_stream (
  "label" STRING,
  "personapplyloanId" BIGINT,
  "personId" BIGINT,
  "loanId" BIGINT,
  "createTime" STRING,
  "org" STRING
) WITH (
  'topic' = 'kafka-PersonApplyLoan',
  'value.format' = 'JSON'
);

-- 16. PersonGuaranteePerson
CREATE STREAM personguaranteeperson_stream (
  "label" STRING,
  "personguaranteepersonId" BIGINT,
  "fromId" BIGINT,
  "toId" BIGINT,
  "createTime" STRING,
  "relation" STRING
) WITH (
  'topic' = 'kafka-PersonGuaranteePerson',
  'value.format' = 'JSON'
);

-- 17. PersonInvestCompany
CREATE STREAM personinvestcompany_stream (
  "label" STRING,
  "personinvestcompanyId" BIGINT,
  "investorId" BIGINT,
  "companyId" BIGINT,
  "ratio" DOUBLE,
  "createTime" STRING
) WITH (
  'topic' = 'kafka-PersonInvestCompany',
  'value.format' = 'JSON'
);

-- 18. PersonOwnAccount
CREATE STREAM personownaccount_stream (
  "label" STRING,
  "personownaccountId" BIGINT,
  "personId" BIGINT,
  "accountId" BIGINT,
  "createTime" STRING
) WITH (
  'topic' = 'kafka-PersonOwnAccount',
  'value.format' = 'JSON'
);

```

## Deltastream Connect to Snowflake
1. Add a Snowflake Store
- Refer to [Snowflake integration documentation](https://docs.deltastream.io/tutorials/integrations/setting-up-and-integrating-snowflake-with-your-organization) for detailed steps

| Parameter                       | Value                                                                                                                          |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| STORE TYPE                      | SNOWFLAKE.                                                                                                                     |
| Name                            | store name; for example: `snowflake_demo`.                                                                                     |
| Region                          | Specifies the region of the Store; for axample: `AWS us-east-1`.                                                               |
| Add One Or More Urls To Connect | URL for Snowflake workspace; For example: `https://<account_id>.snowflakecomputing.com`.                                       |
| Snowflake Cloud Region          | Specifies the region of the Snowflake Cloud; for axample: `AWS us-east-1`.                                                     |
| Account Id                      | Account identifier in the form <orgname>-<account_name>.                                                                       |
| Role Name                       | The name of the access control role to use for the store operations after connecting to Snowflake; for example: `ACCOUNTADMIN` |
| Warehouse Name                  | The name for a Snowflake compute warehouse to use for queries and other store operations that require compute resources.       |
| Username                        | User login name for the Snowflake account.                                                                                     |
| Client Key File                 | Snowflake account's private key in PEM format; for example: `rsa_key.p8`                                                       |
| Key Passphrase                  | If applicable, passphrase for decrypting the Snowflake account's private key.                                                  |

2. Create Snowflake tables using deltastream sql
- **Important Note**  
  When a table is created using the CREATE TABLE statement, a query is automatically generated and executed in DeltaStream. 
  Since DeltaStream currently supports a maximum of 10 queries running simultaneously, it is recommended to create fewer than 10 tables initially. 
  Once the data for these tables is fully imported, you can proceed to create the remaining tables. 
  This approach ensures that the system operates efficiently and avoids hitting the query limit.

```sql
CREATE TABLE ds_account
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>',
  'snowflake.table.name' = 'account',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM account_stream;

CREATE TABLE ds_accountrepayloan
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'accountrepayloan',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM accountrepayloan_stream;

CREATE TABLE ds_accounttransferaccount
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'accounttransferaccount',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM accounttransferaccount_stream;

CREATE TABLE ds_accountwithdrawaccount
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'accountwithdrawaccount',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM accountwithdrawaccount_stream;

CREATE TABLE ds_company
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'company',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM company_stream;

CREATE TABLE ds_companyapplyloan
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'companyapplyloan',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM companyapplyloan_stream;

CREATE TABLE ds_companyguaranteecompany
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'companyguaranteecompany',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM companyguaranteecompany_stream;

CREATE TABLE ds_companyinvestcompany
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'companyinvestcompany',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM companyinvestcompany_stream;

CREATE TABLE ds_companyownaccount
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'companyownaccount',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM companyownaccount_stream;

CREATE TABLE ds_loan
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'loan',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM loan_stream;

CREATE TABLE ds_loandepositaccount
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'loandepositaccount',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM loandepositaccount_stream;

CREATE TABLE ds_medium
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'medium',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM medium_stream;

CREATE TABLE ds_mediumsigninaccount
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'mediumsigninaccount',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM mediumsigninaccount_stream;

CREATE TABLE ds_person
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'person',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM person_stream;

CREATE TABLE ds_personapplyloan
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'personapplyloan',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM personapplyloan_stream;

CREATE TABLE ds_personguaranteeperson
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'personguaranteeperson',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM personguaranteeperson_stream;

CREATE TABLE ds_personinvestcompany
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'personinvestcompany',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM personinvestcompany_stream;

CREATE TABLE ds_personownaccount
WITH
(
  'store' = '<snowflake_store_name>',
  'snowflake.db.name' = '<snowflake_db_name>',
  'snowflake.schema.name' = '<snowflake_schema_name>,
  'snowflake.table.name' = 'personownaccount',
  'snowflake.buffer.millis' = 5000
) AS
SELECT * FROM personownaccount_stream;

```

3. Import data to topics
```bash
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-Account < json_data/Account.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-AccountRepayLoan < json_data/AccountRepayLoan.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-AccountTransferAccount < json_data/AccountTransferAccount.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-AccountWithdrawAccount < json_data/AccountWithdrawAccount.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-Company < json_data/Company.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-CompanyApplyLoan < json_data/CompanyApplyLoan.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-CompanyGuaranteeCompany < json_data/CompanyGuaranteeCompany.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-CompanyInvestCompany < json_data/CompanyInvestCompany.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-CompanyOwnAccount < json_data/CompanyOwnAccount.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-Loan < json_data/Loan.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-LoanDepositAccount < json_data/LoanDepositAccount.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-Medium < json_data/Medium.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-MediumSignInAccount < json_data/MediumSignInAccount.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-Person < json_data/Person.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-PersonApplyLoan < json_data/PersonApplyLoan.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-PersonGuaranteePerson < json_data/PersonGuaranteePerson.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-PersonInvestCompany < json_data/PersonInvestCompany.json
kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-PersonOwnAccount < json_data/PersonOwnAccount.json

```
## Querying Snowflake Using Puppygraph
1. Start Puppygraph Container
```bash
docker run -p 8081:8081 -p 8182:8182 -p 7687:7687 \
-e DATAACCESS_DATA_CACHE_STRATEGY=adaptive \
-e SNOW_USER=<your_snow_username> \
-e SNOW_PWD=<your_snow_password> \
-e SNOW_ACCOUNT_ID=<your_account_id> \
--name puppy --rm -itd puppygraph/puppygraph:stable
```
2. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
- Username: `puppygraph`
- Password: `puppygraph123`

3. Upload the schema:
- Select the file `schema_snowflake.json` in the Upload Graph Schema JSON section and click on Upload.

1. Querying the Graph
- Navigate to the Query panel on the left side. The **Graph Query** tab offers an interactive environment for querying the graph using Gremlin and openCypher.

Example Queries:

Query 1: Query the total number of vertices.
```gremlin
g.V().count()
```

Query 2: Query the total number of edges.
```gremlin
g.E().count()
```

Query 3: Query the accounts owned by a specific company and the transaction records of these accounts.
```gremlin
g.V("Company[237]")
  .outE('CompanyOwnAccount').inV()
  .outE('AccountTransferAccount').inV()
  .path()
```

Query 4: Query the accounts owned by persons born after January 1, 1998, and the loans repaid by these accounts
```gremlin
g.V().hasLabel('Person').has('birthday', gt('1998-01-01'))
  .outE('PersonOwnAccount').inV()
  .outE('AccountRepayLoan').inV()
  .path()
```

## Cleaning up
```bash
docker stop puppy
```

```
bin/kafka-server-stop.sh
```