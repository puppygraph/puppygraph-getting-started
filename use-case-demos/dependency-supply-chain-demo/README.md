# Supply Chain Dependency Risk Management Demo

## Summary

This demo uses PuppyGraph to model the dependencies between internal services and external software packages, making it easy to identify potential supply chain attacks when a third-party package is compromised.
This demo uses PostgreSQL to store all the example data.

**Overview:**

- **`docker-compose.yaml`**: Defines the docker services needed to run the demo. This includes both the PostgreSQL database and the PuppyGraph instance.
- **`data/`**: Contains metadata (dependencies, maintainers, download statistics) of top npm packages, as well as randomly generated internal services and vulnerabilities. The PostgreSQL setup script is located at `data/init.sql`.

## Prerequisites:

- Docker

## Deployment

- Start PostgreSQL and PuppyGraph by running:

```bash
docker compose up -d
```

Example output:

```bash
[+] Running 3/3
✔ Network puppy-postgres        Created
✔ Container postgres            Started
✔ Container puppygraph          Started
```

## PuppyGraph Setup

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:

- Username: `puppygraph`
- Password: `puppygraph123`

2. Upload the schema:

- Select the file `schema.json` in the Upload Graph Schema JSON section and click on Upload.

## Querying the Graph

Navigate to the Query panel on the left side. The Graph Query tab offers an interactive environment for querying the graph using Gremlin and Cypher.

After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization.
You can do this by clicking the **Clear Canvas** button located in the top-right corner of the page.

Example Queries:

1. Find all direct dependencies for the "auth" service

```cypher
MATCH (s:Service{name: "auth"})-[:USES]->(p:Package)
RETURN s, p
```

2. Find all dependencies (direct and indirect) for the "auth" service

```cypher
MATCH (s:Service{name: "auth"})-[:USES|DEPENDS_ON*..10]->(p:Package)
RETURN DISTINCT s, p
```

3. Find services that depend on a vulnerable package with a severity score greater than 5 and sort by decreasing severity

```cypher
MATCH (s:Service)-[:USES|DEPENDS_ON*..10]->(p:Package)-[:VULNERABLE]->(v:Vulnerability)
WHERE v.severity > 5
RETURN DISTINCT s, p, v.severity
ORDER BY v.severity DESC
```

4. Find services that depend on packages that are maintained by maintainers who own a vulnerable package and sort by decreasing severity

```cypher
MATCH (s:Service)-[:USES|DEPENDS_ON*..10]->(p:Package)-[:MAINTAINED_BY]->
  (m:Maintainer)<-[:MAINTAINED_BY]-(vp:Package)-[:VULNERABLE]->(v:Vulnerability)
RETURN DISTINCT s, p, m, vp, v.severity
ORDER BY v.severity DESC
```

## Cleanup and Teardown

- To stop and remove the containers, run:

```bash
docker compose down
```
