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

## Steps to Run
### Loading Data
Start up the Docker container:
```
docker compose up -d
```

We'll start up the Spark shell:
```
docker exec -it spark /opt/spark/bin/spark-sql
```

And create our tables and insert the dummy data:
```
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/person` (
  id STRING, 
  name STRING, 
  age INT
) USING DELTA LOCATION '/delta/demo/person';

CREATE TABLE IF NOT EXISTS delta.`/delta/demo/software` (
  id STRING,
  name STRING,
  lang STRING
) USING DELTA LOCATION '/delta/demo/software';

CREATE TABLE IF NOT EXISTS delta.`/delta/demo/created` (
  id STRING,
  from_id STRING,
  to_id STRING,
  weight DOUBLE
) USING DELTA LOCATION '/delta/demo/created';

CREATE TABLE IF NOT EXISTS delta.`/delta/demo/knows` (
  id STRING, 
  from_id STRING, 
  to_id STRING, 
  weight DOUBLE
) USING DELTA LOCATION '/delta/demo/knows';

INSERT INTO delta.`/delta/demo/person` VALUES
                                         ('v1', 'marko', 29),
                                         ('v2', 'vadas', 27),
                                         ('v4', 'josh', 32),
                                         ('v6', 'peter', 35);

INSERT INTO delta.`/delta/demo/software` VALUES
                                           ('v3', 'lop', 'java'),
                                           ('v5', 'ripple', 'java');

INSERT INTO delta.`/delta/demo/created` VALUES
                                          ('e9', 'v1', 'v3', 0.4),
                                          ('e10', 'v4', 'v5', 1.0),
                                          ('e11', 'v4', 'v3', 0.4),
                                          ('e12', 'v6', 'v3', 0.2);
INSERT INTO delta.`/delta/demo/knows` VALUES
                                        ('e7', 'v1', 'v2', 0.5),
                                        ('e8', 'v1', 'v4', 1.0);

quit;
```

We can now register our tables under Unity Catalog:
```
./register.sh
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

### Sample Query
Input the following query string to find out the creators of the software 'ripple'. The query result would be “josh”:
```cypher
MATCH (p:person)-[:created]->(s:software {name:'ripple'})
RETURN p.name
```

## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
docker compose down --volumes --remove-orphans
```