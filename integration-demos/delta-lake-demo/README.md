# PuppyGraph + Delta Lake = Graph Lakehouse
## Summary
This demo showcases a basic graph analysis workflow by integrating Delta Lake tables with PuppyGraph.

Components of the project:

* Storage: Local Machine
* Data Lakehouse: Delta Lake
* Catalog: Unity Catalog
* Compute engines:
  * Spark – Initial table writes
  * PuppyGraph – Graph query engine for complex, multi-hop graph queries

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

### Loading Data
Start up the Docker container:
```
docker compose up -d
```

We can now register our tables under Unity Catalog:
```
chmod +x create.sh
./create.sh 
```

Once everything is up and running, you can now populate the database:
```
docker compose exec spark bash -lc '/opt/spark/bin/spark-sql -f /sql/load_to_delta.sql'
```

### Modeling the Graph
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

**Gremlin:**
```gremlin
g.V().hasLabel('User').as('user')
  .outE('ACCESS').has('access_level', 'admin').as('edge')
  .inV()
  .path()
  
```
**Cypher:**
```cypher
MATCH path = (u:User)-[r:ACCESS {access_level: 'admin'}]->(ig:InternetGateway)
RETURN u,r,ig
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
**Cypher:**
```cypher
MATCH (u:User)-[r:ACCESS_RECORD]->(ig:InternetGateway)
WHERE id(u)="User[100]" AND r.access_time > datetime("2024-12-01T00:00:00")
RETURN r
ORDER BY r.access_time DESC
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
**Cypher:**
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
**Cypher:**
```cypher
MATCH (ig:InternetGateway)
OPTIONAL MATCH (ig)<-[r:ACCESS_RECORD]-()
WITH ig.region AS region, count(r) AS accessCount
RETURN region, sum(accessCount) AS totalAccessCount

```

5. Find network interfaces that are not protected by any security group, along with their associated virtual machine instances (if any), as these interfaces may pose security risks.

**Cypher:**
```cypher
MATCH (ni:NetworkInterface)
OPTIONAL MATCH (sg:SecurityGroup)-[:PROTECTS]->(ni)
WITH ni, sg
WHERE sg IS NULL
OPTIONAL MATCH (ni)-[:ATTACHED_TO]->(vm:VMInstance)
RETURN ni, vm

```

6. Find all public IP addresses exposed to the internet, along with their associated virtual machine instances, security groups, subnets, VPCs, internet gateways, and users, displaying all these entities in the traversal path.

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
**Cypher:**
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
**Cypher:**
```cypher
MATCH (r:Role)-[:ALLOWS_ACCESS_TO]->(res:Resource)
WITH r, count(res) AS permissionCount
WHERE permissionCount > 4
MATCH path = (vm:VMInstance)-[ar:ASSIGNED_ROLE]->(r)-[at:ALLOWS_ACCESS_TO]->(res:Resource)
RETURN vm,ar,r,at,res

```

8. Find security groups that have ingress rules permitting traffic from any IP address (0.0.0.0/0) to sensitive ports (22 or 3389), and retrieve the associated ingress rules, network interfaces, and virtual machine instances in the traversal path.

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
**Cypher:**
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