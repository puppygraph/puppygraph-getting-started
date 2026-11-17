# OpenTelemetry Service Dependency Graph Demo

## Summary
This demo shows how **OpenTelemetry trace data** can be transformed into a **service-level dependency graph** using **PuppyGraph**.

By modeling service-to-service calls as a graph, we can easily analyze:
- Upstream and downstream service dependencies
- High-traffic service interactions
- Potential latency bottlenecks across microservices

This demo intentionally focuses on a **clean and reproducible service-level view** (simple v1). It can be extended later to span-level graphs or critical path analysis.



## Prerequisites
- Docker
- Docker Compose
- Python 3

## Deployment (Generate Trace Data)
Start the OpenTelemetry Demo stack (with OpenSearch enabled in this environment):

```bash
docker compose up -d
```

Generate traffic via either:
- The demo frontend UI (open in browser and click around), or
- The built-in load generator:

```bash
docker compose up -d load-generator
```

This will produce OpenTelemetry traces stored in OpenSearch.

## Data Preparation (Export CSVs)

### 1) Export service dependency CSVs from OpenSearch

Run the export script:

```bash
python3 tools/export_spans_from_opensearch.py
```

This script:
- Reads OpenTelemetry spans from OpenSearch (`otel-traces-*`)
- Builds span parent/child relationships
- Aggregates them into service-level dependencies
- Produces the following files:
  - `exports/services.csv`
  - `exports/service_edges.csv`

### 2) Copy CSVs into this demo directory

From the OpenTelemetry demo repo root:

```bash
cp exports/services.csv exports/service_edges.csv \
  ~/work/puppygraph-getting-started/use-case-demos/otel-service-dependency/data/
```

Note: This demo repository only includes the derived CSVs + schema + README to keep the scope focused on graph modeling.

## Directory Structure

```
otel-service-dependency/
├── data/
│   ├── init.sql
│   ├── services.csv
│   ├── service_edges.csv
│   └── service_metrics.csv
├── docker-compose.yaml
├── schema.json
└── README.md
```

## Modeling the Graph

The graph schema is defined in:
- `schema.json` (PuppyGraph schema; its catalog points at a PostgreSQL database holding the two CSVs)

Mapping:
- Each row in `data/services.csv` becomes a `Service` vertex
- Each row in `data/service_edges.csv` becomes a `CALLS` edge (`Service -> Service`)
- Edge properties:
  - `call_count`
  - `avg_latency_ms`

## Querying the Graph

In the PuppyGraph Web UI, open the **Query** panel and select **Cypher**. Queries that return a path (`p`) are drawn on the **Graph** tab; queries that return columns appear on the **Table** tab. Click **Clear Canvas** before running the next query.

### 1) Full service dependency graph

Which services call which?

```cypher
MATCH p = (:Service)-[:CALLS]->(:Service)
RETURN p
```

### 2) Blast radius of a service

Which services depend on `product-catalog`, directly or through other services, and would be affected if it went down?

```cypher
MATCH p = (:Service)-[:CALLS*1..5]->(:Service {service_name: 'product-catalog'})
RETURN p
```

### 3) Slowest service interactions

Which calls have the highest average latency? The filter skips calls averaging a minute or more: in this data those are `flagd` streaming connections that stay open until they time out, not slow requests.

As a graph:

```cypher
MATCH p = (:Service)-[r:CALLS]->(:Service)
WHERE r.avg_latency_ms < 60000
RETURN p
ORDER BY r.avg_latency_ms DESC
LIMIT 5
```

As a table, with call volume alongside latency:

```cypher
MATCH (a:Service)-[r:CALLS]->(b:Service)
WHERE r.avg_latency_ms < 60000
RETURN a.service_name AS caller, b.service_name AS callee,
       r.call_count AS calls, r.avg_latency_ms AS avg_latency_ms
ORDER BY avg_latency_ms DESC
LIMIT 5
```

## Cleanup (OpenTelemetry Demo)

If you started the OpenTelemetry demo stack and want to stop everything:

```bash
docker compose down --volumes --remove-orphans
```

## Notes
- This demo stays at the service level for clarity and reproducibility.
- Future extensions (out of scope for v1) could include:
  - Span-level graphs
  - Critical path analysis
  - Trace-as-graph modeling
