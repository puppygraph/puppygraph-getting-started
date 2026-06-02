# Supply Chain Graph Analytics Demo (using PuppyGraph)

## Summary

This demo showcases how to analyze supply chain dependencies and assess risk across a multi-tier supplier network using PuppyGraph's graph querying capabilities, running directly over raw PostgreSQL tables with no ETL required.

By modeling the supply chain as a graph, users can trace complex dependency scenarios such as:

- Suppliers whose failure would impact specific car models
- Parts that represent a single point of failure due to having only one supplier
- Components shared across multiple car models
- Parts with the highest impact across the product catalog

Using Gremlin and Cypher queries, users can traverse the supply chain graph to uncover these risks and gain insights for improving supply chain resilience. This practical approach demonstrates how graph traversal simplifies dependency tracking and risk assessment across complex, multi-level supply chains.

**Overview:**
- **`docker-compose.yml`**: Defines the docker services needed to run the demo. This includes both the PostgreSQL database and the PuppyGraph instance.
- **`data/`**: Contains randomly generated CSV source files for all supply chain entities.
- **`sql/init.sql`**: SQL script for table creation and importing CSV data into PostgreSQL.
- **`schema.json`**: Complete graph mapping configuration for PuppyGraph.

## Prerequisites

- Docker

## Deployment

Start PostgreSQL and PuppyGraph by running:

```bash
docker compose up -d
```

Example output:

```bash
[+] Running 3/3
✔ Network puppy-postgres        Created
✔ Container supply_chain_db     Started
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

After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. You can do this by clicking the **Clear Canvas** button located in the top-right corner of the page.

### Example Queries

#### 1. Supplier Failure Impact

Find all car models affected if a given supplier shuts down.

Gremlin:

```groovy
g.V().has('Supplier', 'name', 'Supplier A')
  .in('is_supplied_by')   // Parts supplied by Supplier A
  .in('is_composed_of')   // Features those Parts compose
  .in('with_feature')     // Car Models those Features belong to
  .values('name').dedup()
```

Cypher:

```cypher
MATCH path = (s:Supplier {name: 'Supplier A'})
  <-[:is_supplied_by]-(p)
  <-[:is_composed_of]-(f)
  <-[:with_feature]-(cm)
RETURN path
```

#### 2. End-to-End Trace (Full Lineage)

Visually map the entire production path from raw material supplier to final car model.

Gremlin:

```groovy
g.V().has('Supplier', 'name', 'Supplier A')
  .in('is_supplied_by')
  .in('is_composed_of')
  .in('with_feature')
  .path()
```

Cypher:

```cypher
MATCH path = (s:Supplier {name: 'Supplier A'})
  <-[:is_supplied_by]-(p)
  <-[:is_composed_of]-(f)
  <-[:with_feature]-(cm)
RETURN path
```

#### 3. Single Point of Failure (SPOF) Audit

Find features that rely on parts sourced from only one supplier.

Gremlin:

```groovy
g.V().hasLabel('Part')
  .where(__.out('is_supplied_by').count().is(1))   // Parts with only 1 supplier
  .in('is_composed_of')                            // Features using those Parts
  .values('name').dedup()
```

Cypher:

```cypher
MATCH (p:Part)-[:is_supplied_by]->(s)
WITH p, count(s) AS supplier_count
WHERE supplier_count = 1
MATCH path = (cm)-[:with_feature]->(f)-[:is_composed_of]->(p)
RETURN path
```

---

#### 4. Bottleneck Parts

Find the parts used by the most features.

Gremlin:

```groovy
g.V().hasLabel('Part')
  .project('PartName', 'ImpactedFeatures')
    .by('name')
    .by(__.in('is_composed_of').count())
  .order().by(select('ImpactedFeatures'), desc).limit(5)
```

Cypher:

```cypher
MATCH (p:Part)
OPTIONAL MATCH (p)<-[:is_composed_of]-(f)
RETURN p.name AS PartName,
       count(f) AS ImpactedFeatures
ORDER BY ImpactedFeatures DESC
LIMIT 5
```

#### 5. Full Bill of Materials

Explode a single car model into its entire component tree (Car → Features → Parts → Suppliers).

```cypher
MATCH path = (cm:CarModel {name: 'Model A'})
  -[:with_feature]->(f:Feature)
  -[:is_composed_of]->(p:Part)
  -[:is_supplied_by]->(s:Supplier)
RETURN path
```

#### 6. Shared Parts Analysis

Discover parts shared between two different car models.

```cypher
MATCH path = (cm1:CarModel)-[:with_feature]->(f1)-[:is_composed_of]->(p:Part)
             <-[:is_composed_of]-(f2)<-[:with_feature]-(cm2:CarModel)
WHERE cm1.name <> cm2.name
  AND cm1.name = 'Model A' AND cm2.name = 'Model B'
RETURN path
LIMIT 50
```

## Cleanup

To stop and remove the containers, run:

```bash
docker compose down
```

## Repo Structure

```
supply-chain-demo/
├── data/          # Randomly generated CSV source files for all entities
├── sql/
│   └── init.sql   # SQL script for table creation + CSV import into PostgreSQL
├── assets/        # Graph schema image generated by PuppyGraph
├── docker-compose.yaml
├── schema.json    # Complete graph mapping configuration for PuppyGraph
└── README.md
```