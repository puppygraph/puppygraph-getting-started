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
CREATE DATABASE security_graph;

CREATE EXTERNAL TABLE security_graph.Users (
  user_id BIGINT,
  username STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.InternetGateways (
  internet_gateway_id BIGINT,
  name STRING
) USING iceberg;

CREATE EXTERNAL TABLE security_graph.UserInternetGatewayAccess (
  user_id BIGINT,
  internet_gateway_id BIGINT
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
SELECT * FROM parquet.`/parquet_data/Users.parquet`;

INSERT INTO security_graph.InternetGateways
SELECT * FROM parquet.`/parquet_data/InternetGateways.parquet`;

INSERT INTO security_graph.UserInternetGatewayAccess
SELECT * FROM parquet.`/parquet_data/UserInternetGatewayAccess.parquet`;

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

## Querying the Graph using Gremlin

- Navigate to the Query panel on the left side. The Gremlin Query tab offers an interactive environment for querying the graph using Gremlin.
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. 
  You can do this by clicking the "Clear" button located in the top-right corner of the page.

Example Queries:
1. Find network interfaces that are not protected by any security group, along with their associated virtual machine instances (if any), as these interfaces may pose security risks.
```gremlin
g.V().hasLabel('NetworkInterface').as('ni')
  .where(
    __.not(
      __.in('PROTECTS').hasLabel('SecurityGroup')
    )
  )
  .optional(
    __.out('ATTACHED_TO').hasLabel('VMInstance').as('vm')
  )
  .path()

```

2. Find all public IP addresses exposed to the internet, along with their associated virtual machine instances, security groups, subnets, VPCs, internet gateways, and users, displaying all these entities in the traversal path.
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

```

3. Find roles that have been granted excessive access permissions, along with their associated virtual machine instances.
```gremlin
g.V().hasLabel('Role').as('role')
 .where(
   __.out('ALLOWS_ACCESS_TO').count().is(gt(4))
 )
 .out('ALLOWS_ACCESS_TO').hasLabel('Resource').as('resource')
 .select('role') 
 .in('ASSIGNED_ROLE').hasLabel('VMInstance').as('vm')
 .path()

```

4. Find security groups that have ingress rules permitting traffic from any IP address (0.0.0.0/0) to sensitive ports (22 or 3389), and retrieve the associated ingress rules, network interfaces, and virtual machine instances in the traversal path.
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

## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
sudo docker compose down --volumes --remove-orphans
```
