# Integrating Apache Hudi Tables and Querying Data Using PuppyGraph

## Summary
This demo showcases a basic graph analysis workflow by integrating Apache Hudi tables with PuppyGraph.

Components of the project:
- Storage: MinIO/S3 – Object store for Hudi data
- Data Lakehouse: Apache Hudi – Brings database functionality to your data lakes
- Catalog: Hive Metastore – Backed by Postgres
- Compute engines:
  - Spark – Initial table writes
  - PuppyGraph – Graph query engine for complex, multi-hop graph queries

This process streamlines storage, data processing and visualization, enabling graph insights from relational data.

## Prerequisites
* [Docker and Docker Compose](https://docs.docker.com/compose/)
* [Python 3 and virtual environment](https://docs.python.org/3/library/venv.html)

## Steps to Run
### Data Preparation
```
python3 -m venv demo
source demo/bin/activate
pip install -r requirements.txt
python3 CsvToParquet.py ./csv_data ./parquet_data
```

### Installing Dependencies
```
mkdir -p lib
curl -L -o lib/postgresql-42.5.1.jar \
  https://repo1.maven.org/maven2/org/postgresql/postgresql/42.5.1/postgresql-42.5.1.jar

curl -L -o lib/hadoop-aws-3.3.4.jar \
  https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar

curl -L -o lib/aws-java-sdk-bundle-1.12.262.jar \
  https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar
```

### Loading Data
Start up the Docker container:
```
docker compose up -d
```

Once everything is up and running, you can now populate the database:
```
docker compose exec spark /opt/spark/bin/spark-sql -f /init.sql
```

### Modeling the Graph
1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
- Username: `puppygraph`
- Password: `puppygraph123`

2. Upload the schema:
- Select the file `schema.json` in the Upload Graph Schema JSON section and click on Upload.

### Querying the Graph using Gremlin and Cypher
- Navigate to the Query panel on the left side. The Graph Query tab offers an interactive environment for querying the graph using Gremlin and Cypher.
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. 
  You can do this by clicking the "Clear Canvas" button located in the top-right corner of the page.

Example Queries:
1. Tracing Admin Access Paths from Users to Internet Gateways.

**Gremlin:**
```gremlin
g.V().hasLabel('User').as('user')
  .outE('ACCESS').has('access_level', 'admin').as('edge')
  .inV()
  .path()
```

2. Retrieve All Access Records for User (user_id=123) Sorted by Access Time.

**Gremlin:**
```gremlin
g.V("User[100]")
  .outE('ACCESS_RECORD')
  .has('access_time', gt("2024-12-01 00:00:00"))
  .order().by('access_time', desc)
  .valueMap()
```

3. Top 10 Users with Highest Access Record Count.

**Gremlin:**
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

4. Aggregate Total Access Count per Region.

**Gremlin:**
```gremlin
g.V().hasLabel('InternetGateway').
  project('region','accessCount').
    by('region').
    by(inE('ACCESS_RECORD').count()).
  group().
    by(select('region')).
    by(__.fold().unfold().select('accessCount').sum()).
  order().by('region') 
```
5. Find all public IP addresses exposed to the internet, along with their associated virtual machine instances, security groups, subnets, VPCs, internet gateways, and users, displaying all these entities in the traversal path.

**Gremlin:**
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

6. Find roles that have been granted excessive access permissions, along with their associated virtual machine instances.

**Gremlin:**
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

7. Find security groups that have ingress rules permitting traffic from any IP address (0.0.0.0/0) to sensitive ports (22 or 3389), and retrieve the associated ingress rules, network interfaces, and virtual machine instances in the traversal path.

**Gremlin:**
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

### Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```
docker compose down --volumes --remove-orphans
```