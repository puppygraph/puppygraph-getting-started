# OpenTelemetry Service Dependency Graph Demo

## Summary
This demo shows how **OpenTelemetry trace data** can be transformed into a **service-level dependency graph** using **PuppyGraph**.

The data is a pre-built snapshot of traces from the [OpenTelemetry Demo](https://github.com/open-telemetry/opentelemetry-demo), a sample microservices web shop maintained by the OpenTelemetry project. The traces were aggregated into one row per service and one row per service-to-service call. In this demo you load that snapshot into PostgreSQL and query it as a graph with PuppyGraph; you do not need to run the OpenTelemetry Demo yourself.

By modeling service-to-service calls as a graph, we can easily analyze:
- Upstream and downstream service dependencies
- High-traffic service interactions
- Potential latency bottlenecks across microservices

This demo intentionally focuses on a **clean and reproducible service-level view** (simple v1). It can be extended later to span-level graphs or critical path analysis.

**Overview:**
- **`docker-compose.yaml`**: Starts PostgreSQL and PuppyGraph.
- **`data/`**: The trace snapshot as CSV files, and `init.sql`, which loads them into PostgreSQL when the container first starts.
- **`schema.json`**: The PuppyGraph schema that maps the PostgreSQL tables to a graph.

## Prerequisites
- Docker

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

## Deployment

From this directory, start PostgreSQL and PuppyGraph:

```bash
docker compose up -d
```

PostgreSQL loads the CSV files from `data/` the first time it starts.

## PuppyGraph Setup

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
   - Username: `puppygraph`
   - Password: `puppygraph123`
2. Upload the schema: on the **Upload Schema** card, click **Upload JSON**, then **Select Schema File**, choose `schema.json` and click **Upload**.

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

## Cleanup and Teardown

To stop and remove the containers and the loaded data:

```bash
docker compose down -v
```

## About the Data Snapshot

The CSV files in `data/` were produced from the [OpenTelemetry Demo](https://github.com/open-telemetry/opentelemetry-demo) as follows. These steps are background only; you do not need to repeat them to run this demo.

1. The OpenTelemetry Demo was run with traces stored in OpenSearch, and traffic was generated with its built-in load generator.
2. Spans were read from OpenSearch (`otel-traces-*`) and linked by their parent/child relationships.
3. Each call from one service to another was aggregated into one row of `service_edges.csv`, with the number of calls (`call_count`) and their average latency in milliseconds (`avg_latency_ms`). `services.csv` lists the services.
4. `service_metrics.csv` holds per-service span counts and latencies from the same traces. It is not part of the graph schema.

The snapshot only covers the calls captured during that run, so a few services have no edges (for example `quote` and `image-provider`). The calls to `flagd` with an average latency of around 600,000 ms are its long-lived streaming connections, not slow requests.

## Notes
- This demo stays at the service level for clarity and reproducibility.
- Future extensions (out of scope for v1) could include:
  - Span-level graphs
  - Critical path analysis
  - Trace-as-graph modeling
