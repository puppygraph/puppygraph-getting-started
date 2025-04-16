# Integrating DeltaStream with Databricks and Querying Data Using PuppyGraph

## Summary
This demo demonstrates the integration of DeltaStream with Databricks by importing data from Kafka, followed by querying Databricks data using PuppyGraph.  
The workflow enables users to process, store, and visualize data seamlessly with a graph database interface.

## Prerequisites

- Docker
- Kafka
- Databricks

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

## Deltastream Connect to Databricks
1. Create s3 bucket for kafka topics
```bash
aws s3api put-object --bucket <your-bucket-name> --key your-directory/account
aws s3api put-object --bucket <your-bucket-name> --key your-directory/accountrepayloan
aws s3api put-object --bucket <your-bucket-name> --key your-directory/accounttransferaccount
aws s3api put-object --bucket <your-bucket-name> --key your-directory/accountwithdrawaccount
aws s3api put-object --bucket <your-bucket-name> --key your-directory/company
aws s3api put-object --bucket <your-bucket-name> --key your-directory/companyapplyloan
aws s3api put-object --bucket <your-bucket-name> --key your-directory/companyguaranteecompany
aws s3api put-object --bucket <your-bucket-name> --key your-directory/companyinvestcompany/
aws s3api put-object --bucket <your-bucket-name> --key your-directory/companyownaccount/
aws s3api put-object --bucket <your-bucket-name> --key your-directory/loan/
aws s3api put-object --bucket <your-bucket-name> --key your-directory/loandepositaccount/
aws s3api put-object --bucket <your-bucket-name> --key your-directory/medium/
aws s3api put-object --bucket <your-bucket-name> --key your-directory/mediumsigninaccount/
aws s3api put-object --bucket <your-bucket-name> --key your-directory/person/
aws s3api put-object --bucket <your-bucket-name> --key your-directory/personapplyloan/
aws s3api put-object --bucket <your-bucket-name> --key your-directory/personguaranteeperson/
aws s3api put-object --bucket <your-bucket-name> --key your-directory/personinvestcompany/
aws s3api put-object --bucket <your-bucket-name> --key your-directory/personownaccount/
```

2. Add a Databricks Store
- Refer to [Databricks integration documentation](https://docs.deltastream.io/tutorials/integrations/setting-up-and-integrating-databricks-with-your-organization) for detailed steps

| Parameter                       | Value                                                                                                                                            |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| STORE TYPE                      | DATABRICKS.                                                                                                                                      |
| Name                            | store name; for example: `databricks_demo`.                                                                                                      |
| Region                          | Specifies the region of the Store; for axample: `AWS us-east-1`.                                                                                 |
| Add One Or More Urls To Connect | URL for Databricks workspace; For example: `https://xxx-xxxxxxx-xxxx.cloud.databricks.com`.                                                      |
| Warehouse ID                    | The ID for a Databricks SQL warehouse in your Databricks workspace; for example: `dfaaaaaaaabbbbb`.                                              |
| Databricks Cloud Region         | The AWS region in which the Cloud S3 Bucket exists.                                                                                              |
| Cloud S3 Bucket                 | An AWS S3 bucket that is connected as an external location in your Databricks workspace; for example: `databricks-workspace-stack-xxxxx-bucket`  |
| App Token                       | The Databricks access token for your user in your Databricks workspace.                                                                          |
| Access Key ID                   | Access key associated with the AWS account in which the Cloud S3 Bucket exists.                                                                  |
| Secret Access Key               | Secret access key associated with the AWS account in which the Cloud S3 Bucket exists.                                                           |

3. Create Databricks tables via Deltastream SQL
- **Important Note**  
  When a table is created using the CREATE TABLE statement, a query is automatically generated and executed in DeltaStream.
  Since DeltaStream currently supports a maximum of 10 queries running simultaneously, it is recommended to create fewer than 10 tables initially.
  Once the data for these tables is fully imported, you can proceed to create the remaining tables.
  This approach ensures that the system operates efficiently and avoids hitting the query limit.

```sql
CREATE TABLE ds_account
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'account',
  'table.data.file.location' = 's3://<your_bucket_path>/account/'
) AS
SELECT * FROM account_stream;

CREATE TABLE ds_accountrepayloan
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'accountrepayloan',
  'table.data.file.location' = 's3://<your_bucket_path>/accountrepayloan/'
) AS
SELECT * FROM accountrepayloan_stream;

CREATE TABLE ds_accounttransferaccount
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'accounttransferaccount',
  'table.data.file.location' = 's3://<your_bucket_path>/accounttransferaccount/'
) AS
SELECT * FROM accounttransferaccount_stream;

CREATE TABLE ds_accountwithdrawaccount
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'accountwithdrawaccount',
  'table.data.file.location' = 's3://<your_bucket_path>/accountwithdrawaccount/'
) AS
SELECT * FROM accountwithdrawaccount_stream;

CREATE TABLE ds_company
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'company',
  'table.data.file.location' = 's3://<your_bucket_path>/company/'
) AS
SELECT * FROM company_stream;

CREATE TABLE ds_companyapplyloan
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'companyapplyloan',
  'table.data.file.location' = 's3://<your_bucket_path>/companyapplyloan/'
) AS
SELECT * FROM companyapplyloan_stream;

CREATE TABLE ds_companyguaranteecompany
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'companyguaranteecompany',
  'table.data.file.location' = 's3://<your_bucket_path>/companyguaranteecompany/'
) AS
SELECT * FROM companyguaranteecompany_stream;

CREATE TABLE ds_companyinvestcompany
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'companyinvestcompany',
  'table.data.file.location' = 's3://<your_bucket_path>/companyinvestcompany/'
) AS
SELECT * FROM companyinvestcompany_stream;

CREATE TABLE ds_companyownaccount
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'companyownaccount',
  'table.data.file.location' = 's3://<your_bucket_path>/companyownaccount/'
) AS
SELECT * FROM companyownaccount_stream;

CREATE TABLE ds_loan
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'loan',
  'table.data.file.location' = 's3://<your_bucket_path>/loan/'
) AS
SELECT * FROM loan_stream;

CREATE TABLE ds_loandepositaccount
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'loandepositaccount',
  'table.data.file.location' = 's3://<your_bucket_path>/loandepositaccount/'
) AS
SELECT * FROM loandepositaccount_stream;

CREATE TABLE ds_medium
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'medium',
  'table.data.file.location' = 's3://<your_bucket_path>/medium/'
) AS
SELECT * FROM medium_stream;

CREATE TABLE ds_mediumsigninaccount
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'mediumsigninaccount',
  'table.data.file.location' = 's3://<your_bucket_path>/mediumsigninaccount/'
) AS
SELECT * FROM mediumsigninaccount_stream;

CREATE TABLE ds_person
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'person',
  'table.data.file.location' = 's3://<your_bucket_path>/person/'
) AS
SELECT * FROM person_stream;

CREATE TABLE ds_personapplyloan
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'personapplyloan',
  'table.data.file.location' = 's3://<your_bucket_path>/personapplyloan/'
) AS
SELECT * FROM personapplyloan_stream;

CREATE TABLE ds_personguaranteeperson
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'personguaranteeperson',
  'table.data.file.location' = 's3://<your_bucket_path>/personguaranteeperson/'
) AS
SELECT * FROM personguaranteeperson_stream;

CREATE TABLE ds_personinvestcompany
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'personinvestcompany',
  'table.data.file.location' = 's3://<your_bucket_path>/personinvestcompany/'
) AS
SELECT * FROM personinvestcompany_stream;

CREATE TABLE ds_personownaccount
WITH
(
  'store' = '<databricks_store_name>',
  'databricks.catalog.name' = '<databricks_catalog_name>',
  'databricks.schema.name' = '<databricks_schema_name>',
  'databricks.table.name' = 'personownaccount',
  'table.data.file.location' = 's3://<your_bucket_path>/personownaccount/'
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
## Querying Databricks Using Puppygraph
1. Start Puppygraph Container
```bash
docker run -p 8081:8081 -p 8182:8182 -p 7687:7687 \
-e DATAACCESS_DATA_CACHE_STRATEGY=adaptive \
-e DATABRICKS_HOST=<your_host> \
-e DATABRICKS_TOKEN=<your_token> \
-e DATABRICKS_S3_ACCESSKEY=<your_s3_accesskey> \
-e DATABRICKS_S3_SECRETKEY=<your_s3_secretkey> \
--name puppy --rm -itd puppygraph/puppygraph:stable
```
2. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
- Username: `puppygraph`
- Password: `puppygraph123`

3. Upload the schema:
- Select the file `schema_databricks.json` in the Upload Graph Schema JSON section and click on Upload.

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
1. Stop the PuppyGraph container:
```bash
docker stop puppy
```
2. Stop Kafka server:
```
bin/kafka-server-stop.sh
```