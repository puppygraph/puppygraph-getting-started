## **Supply Chain Graph Analytics - Use case Demo**
This project serves as an official use-case demonstration of how PuppyGraph rapidly transforms complex relational data into an analyzable graph structure, 
(therefore enabling advanced dependency tracking and risk assessment in a supply chain context)

The primary objective is to solve the critical business challenge of tracing multi-level dependencies

### **Architecture and Data Integration**
The data remains consolidated in its original source while PuppyGraph overlays the graph structure for querying.

**Data Flow:**
* Relational Source: PostgreSQL stores raw tables
* Graph Mapping: schema.json config file automatically instructs the PuppyGraph Engine on how to:
    * map Postgres tables into graph nodes
    * link tables into relationships (edges)
* Real-Time Analysis: The PuppyGraph Engine uses the JDBC connection to execute Gremlin or Cypher traversals
  directly against the relational data (provides real-time analytics without data duplication)
---
### **Examples of Analytical Use-cases (Gremlin and Cypher Queries)**

#### **1. Supplier Failure Impact (Ripple Effect)**

Ques: If *Supplier A* shuts down, which car models are afffected?
```groovy
g.V().has('Supplier', 'name', 'Supplier A')
  .in('is_supplied_by')   //find Parts supplied by A
  .in('is_composed_of')   //find Features those Parts compose
  .in('with_feature')     //find Car Models those Features belong to
  .values('name').dedup()
```

```cypher
MATCH (s:Supplier {name: 'Supplier A'})
MATCH (s)<-[:is_supplied_by]-(p)  //find Parts supplied by A
MATCH (p)<-[:is_composed_of]-(f)  //find Features those Parts compose
MATCH (f)<-[:with_feature]-(cm)   //find Car Models those Features belong to
RETURN DISTINCT cm.name
```

Cypher query to visualize the "Blast Radius" - visualizes affected actual paths of impact (from supplier to feature):
(Essentially highlights a specific subgraph "infected" by a failure)
```cypher
MATCH path = (s:Supplier {name: 'Supplier A'})
  <-[:is_supplied_by]-(p)
  <-[:is_composed_of]-(f)
  <-[:with_feature]-(cm)
RETURN path
```

* SQL would have required four-table `JOIN` for this
  * And this complexity grows exponentially with each added layer of dependency
* Graph can just walk the dependency chain

#### **2. End-to-end Trace (Full Lineage)**

Ques: Visually map the entire production path from raw material supplier to final car model
```groovy
g.V().has('Supplier', 'name', 'Supplier A')
  .in('is_supplied_by')
  .in('is_composed_of')
  .in('with_feature')
  .path()
```

```cypher
MATCH path = (s:Supplier {name: 'Supplier A'})
  <-[:is_supplied_by]-(p)
  <-[:is_composed_of]-(f)
  <-[:with_feature]-(cm)
RETURN path
```

* SQL would require a complex 4-table `JOIN`
* Graph simply needs a 3-hop traversal to return full path

#### **3. Single Point of Failure (SPOF) Audit**

Ques: Find names of Featuers relying on parts from *only one* supplier
```groovy
g.V().hasLabel('Part')
  .where(__.out('is_supplied_by').count().is(1))   //filter for Parts with only 1 supplier
  .in('is_composed_of')   //find Features that use these risky Parts
  .values('name').dedup()
```

```cypher
MATCH (p:Part)
// Filter for Parts with exactly 1 supplier
MATCH (p)-[:is_supplied_by]->(s)
WITH p, count(s) AS supplier_count
WHERE supplier_count = 1

// Find Features that use these risky Parts
MATCH (p)<-[:is_composed_of]-(f:Feature)
RETURN DISTINCT f.name
```
Cypher query for this high-risk dependency visualization:
```cypher
MATCH (p:Part)
// 1. Find parts with only one supplier (SPOF)
MATCH (p)-[:is_supplied_by]->(s)
WITH p, count(s) as supplier_count
WHERE supplier_count = 1

// 2. Return the path from that risky part up to the car
MATCH path = (cm)-[:with_feature]->(f)-[:is_composed_of]->(p)
RETURN path
```

* SQL needs complex conditional filtering:
    * group parts by supplier
    * filter for parts where supplier count is one `HAVING COUNT(supplier) = 1`
    * join restricted result back to Features table
* We just use a simple traversal filter (`WHERE`) to find nodes lacking alternate paths

#### **4. Identify "bottleneck" parts (Centrality)**

Ques: Which parts aremost crucial? (Used by the most Features?)
```groovy
g.V().hasLabel('Part')
  .project('PartName', 'ImpactedFeatures')
    .by('name')
    .by(__.in('is_composed_of').count())   //count incoming edges (Features)
  .order().by(select('ImpactedFeatures'), desc).limit(5)
```

```cypher
MATCH (p:Part)
OPTIONAL MATCH (p)<-[:is_composed_of]-(f)
RETURN p.name AS PartName, 
       count(f) AS ImpactedFeatures   //count incoming edges (Features)
ORDER BY ImpactedFeatures DESC
LIMIT 5
```

* SQL would require heavy aggregation (`GROUP BY` and `COUNT`) across multuple joined tables
    * This forces DB to materialize large temporary tables
    * Slow process + locks up resources
* We can calculate **degree centrality** directly on graph

#### **5. True Cost Roll-up per feature**

Ques: Calculate the total manufacturing cost of a specific feature (by summing prices of all it's raw parts)
```groovy
g.V().hasLabel('Feature')
  .project('Feature', 'TotalCost')
    .by('name')
    .by(__.out('is_composed_of').values('price').sum())
  .order().by(select('TotalCost'), desc)
```

```cypher
MATCH (f:Feature)
OPTIONAL MATCH (f)-[:is_composed_of]->(p)
RETURN f.name AS Feature, 
       sum(p.price) AS TotalCost
ORDER BY TotalCost DESC
```

* If SQL query for summing across heirarchical joins is not written perfectly it can lead to "Cartesian product" problem
  * Can lead to duplicate counts (so incorrect financial metrics)
* We can simply traverse graph structure and use built-in sum() on price attribute

### **Examples of some other visualizations (using Cypher queries)**

#### **1. Model X-Ray (Full Bill of Materials)
Goal: Visually explode a single car model into its entire component tree (Car → Features → Parts → Suppliers)
```cypher
MATCH path = (cm:CarModel {name: 'Model A'})
  -[:with_feature]->(f:Feature)
  -[:is_composed_of]->(p:Part)
  -[:is_supplied_by]->(s:Supplier)
RETURN path
```
This visualizes supply chain depth

#### **Shared Parts Analysis ("butterfly" graph)** 
Goal: Discover parts that are shared between two different Car Models
```cypher
MATCH path = (cm1:CarModel)-[:with_feature]->(f1)-[:is_composed_of]->(p:Part)
             <-[:is_composed_of]-(f2)<-[:with_feature]-(cm2:CarModel)
WHERE cm1.name <> cm2.name
//we'll also filter for a specific pair of models for this example
AND cm1.name = 'Model A' AND cm2.name = 'Model B'
RETURN path
LIMIT 50  //give max 50 paths (to prevent "hairballs")
```
---
### **Steps for Local setup and Replication**
> Pre-req: **Docker Desktop** has to installed and running on your system

1. Clone this repo
```bash
git clone https://github.com/yeshapan/supply-chain-demo.git
cd supply-chain-demo
```
2. Launch the stack
```
docker-compose up
```
3. Access the dashboard
   * Wait for engine to boot + schema to load
   * Open browser to: `http://localhost:8081`
   * Login credentials to PuppyGraph UI:
       * username: puppygraph
       * password: puppygraph123
   
4. Run queries!! 🥳
---
### Repo structure
```bash
supply-chain-demo/
├── data/                       #raw CSV source files for all entities (nodes and edges)
├── sql/
│   └── init.sql                #SQL script for table creation + import CSV data into Postgres
├── assets/                     #contains image of graph schema generated by PuppyGraph
├── docker-compose.yml          #orchestrates the Postgres and PuppyGraph services
├── schema.json                 #complete graph mapping configuration for PuppyGraph   
└── README.md                   #some project documentation
```
