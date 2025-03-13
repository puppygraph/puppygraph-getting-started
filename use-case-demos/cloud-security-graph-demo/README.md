#  Security Graph Demo

## Summary
This demo showcases how to analyze and visualize network security configurations within a cloud environment using PuppyGraph's powerful graph querying capabilities.  

By modeling the network infrastructure as a graph, users can identify potential security risks, such as:
- Public IP addresses exposed to the internet
- Network interfaces not protected by any security group
- Roles granted excessive access permissions
- Security groups with overly permissive ingress rules

Using Gremlin queries, users can traverse the security graph to uncover these issues and gain insights for improving the network's security posture. This practical approach assists in proactive security auditing and optimization in complex cloud environments.

- **`README.md`**: Provides an overview of the project, including setup instructions and key details about the demo.
- **`docker-compose.yaml`**: Sets up the necessary services using Docker, defining containers and environments such as databases and applications for running the demo.
- **`CsvToParquet.py`**: Converts CSV files into Parquet format for easier data import into Iceberg.
- **`csv_data/`**:  Contains randomly generated CSV files representing network entities and configurations. These files are used as input for converting to Parquet format and then imported into Iceberg to model the security graph.

## Prerequisites:
- Docker
- Docker Compose
- Python 3

## Note:
The Demo Data Preparation step below populate some example data for demonstration purposes.
For real-world use cases, you can directly connect your existing data sources to PuppyGraph without the need for data preparation.

## Data Preparation
- We will create a virtual environment and run the python script `CsvToParquet.py` to convert CSV files to Parquet format. On some Linux distributions, you may need to install `python3-venv` first.
```bash
# On some Linux distributions, install `python3-venv` first.
sudo apt-get update
sudo apt-get install python3-venv
```

- Create a virtual environment, activate it and install the necessary packages.
```bash
python3 -m venv demo_venv
source demo_venv/bin/activate
pip install pandas pyarrow
```

- Convert CSV files to Parquet format:
```bash
python3 CsvToParquet.py ./csv_data ./parquet_data
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

CREATE EXTERNAL TABLE security_graph.Users (
  user_id               BIGINT,
  username              STRING,
  email                 STRING,
  phone                 STRING,
  created_at            TIMESTAMP,
  last_login            TIMESTAMP,
  account_status        STRING,
  authentication_method STRING,
  failed_login_attempts INT
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.InternetGateways (
  internet_gateway_id   BIGINT,
  name                  STRING,
  region                STRING,
  status                STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.UserInternetGatewayAccess (
  user_id               BIGINT,
  internet_gateway_id   BIGINT,
  access_level          STRING,
  granted_at            TIMESTAMP,
  expires_at            TIMESTAMP,
  last_accessed_at      TIMESTAMP
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.UserInternetGatewayAccessLog (
  log_id                BIGINT,
  user_id               BIGINT,
  internet_gateway_id   BIGINT,
  access_time           TIMESTAMP
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.VPCs (
  vpc_id BIGINT,
  name STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.InternetGatewayVPC (
  internet_gateway_id BIGINT,
  vpc_id BIGINT
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.Subnets (
  subnet_id BIGINT,
  vpc_id BIGINT,
  name STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.SecurityGroups (
  security_group_id BIGINT,
  name STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.SubnetSecurityGroup (
  subnet_id BIGINT,
  security_group_id BIGINT
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.NetworkInterfaces (
  network_interface_id BIGINT,
  subnet_id BIGINT,
  security_group_id BIGINT,
  name STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.VMInstances (
  vm_instance_id BIGINT,
  network_interface_id BIGINT,
  role_id BIGINT,
  name STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.Roles (
  role_id BIGINT,
  name STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.Resources (
  resource_id BIGINT,
  name STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.RoleResourceAccess (
  role_id BIGINT,
  resource_id BIGINT
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.PublicIPs (
  public_ip_id BIGINT,
  ip_address STRING,
  network_interface_id BIGINT
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.PrivateIPs (
  private_ip_id BIGINT,
  ip_address STRING,
  network_interface_id BIGINT
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.IngressRules (
  ingress_rule_id BIGINT,
  security_group_id BIGINT,
  protocol STRING,
  port_range STRING,
  source STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.IngressRuleInternetGateway (
  ingress_rule_id BIGINT,
  internet_gateway_id BIGINT
) USING iceberg;

INSERT INTO security_graph.Users
SELECT
    user_id,
    username,
    email,
    phone,
    CAST(created_at AS TIMESTAMP),
    CAST(last_login AS TIMESTAMP),
    account_status,
    authentication_method,
    failed_login_attempts
FROM parquet.`/parquet_data/Users.parquet`;

INSERT INTO security_graph.InternetGateways
SELECT * FROM parquet.`/parquet_data/InternetGateways.parquet`;

INSERT INTO security_graph.UserInternetGatewayAccess
SELECT
    user_id,
    internet_gateway_id,
    access_level,
    CAST(granted_at AS TIMESTAMP),
    CAST(expires_at AS TIMESTAMP),
    CAST(last_accessed_at AS TIMESTAMP)
FROM parquet.`/parquet_data/UserInternetGatewayAccess.parquet`;

INSERT INTO security_graph.UserInternetGatewayAccessLog
SELECT
    log_id,
    user_id,
    internet_gateway_id,
    CAST(access_time AS TIMESTAMP)
FROM parquet.`/parquet_data/UserInternetGatewayAccessLog.parquet`;

INSERT INTO security_graph.VPCs
SELECT * FROM parquet.`/parquet_data/VPCs.parquet`;

INSERT INTO security_graph.InternetGatewayVPC
SELECT * FROM parquet.`/parquet_data/InternetGatewayVPC.parquet`;

INSERT INTO security_graph.Subnets
SELECT * FROM parquet.`/parquet_data/Subnets.parquet`;

INSERT INTO security_graph.SecurityGroups
SELECT * FROM parquet.`/parquet_data/SecurityGroups.parquet`;

INSERT INTO security_graph.SubnetSecurityGroup
SELECT * FROM parquet.`/parquet_data/SubnetSecurityGroup.parquet`;

INSERT INTO security_graph.NetworkInterfaces
SELECT * FROM parquet.`/parquet_data/NetworkInterfaces.parquet`;

INSERT INTO security_graph.VMInstances
SELECT * FROM parquet.`/parquet_data/VMInstances.parquet`;

INSERT INTO security_graph.Roles
SELECT * FROM parquet.`/parquet_data/Roles.parquet`;

INSERT INTO security_graph.Resources  
SELECT * FROM parquet.`/parquet_data/Resources.parquet`;

INSERT INTO security_graph.RoleResourceAccess  
SELECT * FROM parquet.`/parquet_data/RoleResourceAccess.parquet`;

INSERT INTO security_graph.PublicIPs
SELECT * FROM parquet.`/parquet_data/PublicIPs.parquet`;

INSERT INTO security_graph.PrivateIPs 
SELECT * FROM parquet.`/parquet_data/PrivateIPs.parquet`;

INSERT INTO security_graph.IngressRules 
SELECT * FROM parquet.`/parquet_data/IngressRules.parquet`;

INSERT INTO security_graph.IngressRuleInternetGateway 
SELECT * FROM parquet.`/parquet_data/IngressRuleInternetGateway.parquet`;

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

## Querying the Graph using Gremlin and Cypher

- Navigate to the Query panel on the left side. The Graph Query tab offers an interactive environment for querying the graph using Gremlin and Cypher.
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. 
  You can do this by clicking the "Clear Canvas" button located in the top-right corner of the page.

Example Queries:
1. Tracing Admin Access Paths from Users to Internet Gateways.

**gremlin:**
```gremlin
g.V().hasLabel('User').as('user')
  .outE('ACCESS').has('access_level', 'admin').as('edge')
  .inV()
  .path()
  
```
**cypher:**
```cypher
MATCH path = (u:User)-[r:ACCESS {access_level: 'admin'}]->(ig:InternetGateway)
RETURN u,r,ig
```

2. Retrieve All Access Records for User (user_id=123) Sorted by Access Time.

**gremlin:**
```gremlin
g.V("User[100]")
  .outE('ACCESS_RECORD')
  .has('access_time', gt("2024-12-01 00:00:00"))
  .order().by('access_time', desc)
  .valueMap()

```
**cypher:**
```cypher
MATCH (u:User)-[r:ACCESS_RECORD]->(ig:InternetGateway)
WHERE id(u)="User[100]" AND r.access_time > datetime("2024-12-01T00:00:00")
RETURN r
ORDER BY r.access_time DESC
```

3. Top 10 Users with Highest Access Record Count.

**gremlin:**
```gremlin
g.V().hasLabel('User')
  .project('user','accessCount')
    .by(valueMap('user_id','username','phone','email'))
    .by(
      outE('ACCESS_RECORD')
        .has('access_time', gt("2024-01-01 00:00:00"))
        .has('access_time', lt("2025-3-31 23:59:59"))
        .count()
    )
  .order().by(select('accessCount'), desc)
  .limit(10)

```
**cypher:**
```cypher
MATCH (u:User)
OPTIONAL MATCH (u)-[r:ACCESS_RECORD]->(ig:InternetGateway)
WHERE r.access_time >= datetime("2024-01-01T00:00:00") 
  AND r.access_time <= datetime("2025-03-31T23:59:59")
WITH u, count(r) AS accessCount
RETURN id(u) AS user_id, u.username AS username, u.phone AS phone, u.email AS email, accessCount
ORDER BY accessCount DESC
LIMIT 10

```
4. Aggregate Total Access Count per Region.

**gremlin:**
```gremlin
g.V().hasLabel('InternetGateway').
  project('region','accessCount').
    by('region').
    by(inE('ACCESS_RECORD').count()).
  group().
    by(select('region')).
    by(__.fold().unfold().select('accessCount').sum()).
  order().by(region')
    
```
**cypher:**
```cypher
MATCH (ig:InternetGateway)
OPTIONAL MATCH (ig)<-[r:ACCESS_RECORD]-()
WITH ig.region AS region, count(r) AS accessCount
RETURN region, sum(accessCount) AS totalAccessCount

```

5. Find network interfaces that are not protected by any security group, along with their associated virtual machine instances (if any), as these interfaces may pose security risks.

**cypher:**
```cypher
MATCH (ni:NetworkInterface)
OPTIONAL MATCH (sg:SecurityGroup)-[:PROTECTS]->(ni)
WITH ni, sg
WHERE sg IS NULL
OPTIONAL MATCH (ni)-[:ATTACHED_TO]->(vm:VMInstance)
RETURN ni, vm

```

6. Find all public IP addresses exposed to the internet, along with their associated virtual machine instances, security groups, subnets, VPCs, internet gateways, and users, displaying all these entities in the traversal path.

**gremlin:**
```gremlin 
  g.V().hasLabel('PublicIP').as('ip')
  .in('HAS_PUBLIC_IP').as('ni')
  .in('PROTECTS').hasLabel('SecurityGroup').as('sg')
  .out('HAS_RULE').hasLabel('IngressRule').as('rule')
  .where(
    __.out('ALLOWS_TRAFFIC_FROM').hasLabel('InternetGateway')
  )
  .select('ni')
    .out('ATTACHED_TO').hasLabel('VMInstance').as('vm')
  .select('ni')
    .in('HOSTS_INTERFACE').hasLabel('Subnet').as('subnet')
    .in('CONTAINS').hasLabel('VPC').as('vpc')
    .in('GATEWAY_TO').hasLabel('InternetGateway').as('igw')
    .in('ACCESS').hasLabel('User').as('user')
  .path()
  .limit(1000)
  
```
**cypher:**
```cypher
MATCH (ip:PublicIP)<-[hp:HAS_PUBLIC_IP]-(ni:NetworkInterface)
MATCH (ni)<-[pr:PROTECTS]-(sg:SecurityGroup)
MATCH (sg)-[hr:HAS_RULE]->(rule:IngressRule)-[atf:ALLOWS_TRAFFIC_FROM]->(igRule:InternetGateway)
MATCH (ni)-[at:ATTACHED_TO]->(vm:VMInstance)
MATCH (ni)<-[hi:HOSTS_INTERFACE]-(subnet:Subnet)
MATCH (subnet)<-[con:CONTAINS]-(vpc:VPC)
MATCH (vpc)<-[gt:GATEWAY_TO]-(ig:InternetGateway)
MATCH (ig)<-[ac:ACCESS]-(user:User)
RETURN ip, hp, ni, hr, rule, atf, igRule,
       at, vm,
       hi, subnet, con, vpc, gt, ig, ac, user
LIMIT 1000

```

7. Find roles that have been granted excessive access permissions, along with their associated virtual machine instances.

**gremlin:**
```gremlin
g.V().hasLabel('Role').as('role')
 .where(
   __.out('ALLOWS_ACCESS_TO').count().is(gt(4L))
 )
 .out('ALLOWS_ACCESS_TO').hasLabel('Resource').as('resource')
 .select('role') 
 .in('ASSIGNED_ROLE').hasLabel('VMInstance').as('vm')
 .path()

```
**cypher:**
```cypher
MATCH (r:Role)-[:ALLOWS_ACCESS_TO]->(res:Resource)
WITH r, count(res) AS permissionCount
WHERE permissionCount > 4
MATCH path = (vm:VMInstance)-[ar:ASSIGNED_ROLE]->(r)-[at:ALLOWS_ACCESS_TO]->(res:Resource)
RETURN vm,ar,r,at,res

```

8. Find security groups that have ingress rules permitting traffic from any IP address (0.0.0.0/0) to sensitive ports (22 or 3389), and retrieve the associated ingress rules, network interfaces, and virtual machine instances in the traversal path.

**gremlin:**
```gremlin
g.V().hasLabel('SecurityGroup').as('sg')
  .out('HAS_RULE')
    .has('source', '0.0.0.0/0')
    .has('port_range', P.within('22', '3389'))
    .hasLabel('IngressRule').as('rule')
  .in('HAS_RULE').as('sg')
  .out('PROTECTS').hasLabel('NetworkInterface').as('ni')
  .out('ATTACHED_TO').hasLabel('VMInstance').as('vm')
  .path()

```
**cypher:**
```cypher
MATCH (sg:SecurityGroup)-[hr:HAS_RULE]->(rule:IngressRule)
WHERE rule.source = '0.0.0.0/0' AND rule.port_range IN ['22','3389']
MATCH (sg)-[p:PROTECTS]->(ni:NetworkInterface)
MATCH (ni)-[at:ATTACHED_TO]->(vm:VMInstance)
RETURN sg, hr, rule, p, ni, at, vm

```


## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
docker compose down --volumes --remove-orphans
```
