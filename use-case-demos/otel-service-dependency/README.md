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

Generate traffic via either:
	•	The demo frontend UI (open in browser and click around), or
	•	The built-in load generator:

docker compose up -d load-generator

This will produce OpenTelemetry traces stored in OpenSearch.



Data Preparation (Export CSVs)

1) Export service dependency CSVs from OpenSearch

Run the export script:

python3 tools/export_spans_from_opensearch.py

This script:
	•	Reads OpenTelemetry spans from OpenSearch (otel-traces-*)
	•	Builds span parent/child relationships
	•	Aggregates them into service-level dependencies
	•	Produces the following files:
	•	exports/services.csv
	•	exports/service_edges.csv

2) Copy CSVs into this demo directory

From the OpenTelemetry demo repo root:

cp exports/services.csv exports/service_edges.csv \
  ~/work/puppygraph-getting-started/use-case-demos/otel-service-dependency/data/

Note: This demo repository only includes the derived CSVs + schema + README to keep the scope focused on graph modeling.



Directory Structure

otel-service-dependency/
├── data/
│   ├── services.csv
│   └── service_edges.csv
├── schema/
│   └── graph.yaml
└── README.md




Modeling the Graph

The graph schema is defined in:
	•	schema/graph.yaml

Mapping:
	•	Each row in data/services.csv becomes a Service vertex
	•	Each row in data/service_edges.csv becomes a CALLS edge (Service -> Service)
	•	Edge properties:
	•	call_count
	•	avg_latency_ms



Querying the Graph (Gremlin Examples)

Exact query syntax may vary slightly depending on how you load the schema, but the intent is the same.

1) Count services

g.V().hasLabel('Service').count()

2) List all services

g.V().hasLabel('Service').values('service_name')

3) Find downstream dependencies of a service

Question: Which services are called by frontend?

g.V().hasLabel('Service').has('service_name', 'frontend')
  .outE('CALLS')
  .project('to','call_count','avg_latency_ms')
  .by(inV().values('service_name'))
  .by(values('call_count'))
  .by(values('avg_latency_ms'))

4) Identify highest-volume service interactions

g.E().hasLabel('CALLS')
  .order().by('call_count', desc)
  .limit(20)

5) Identify latency bottlenecks

g.E().hasLabel('CALLS')
  .order().by('avg_latency_ms', desc)
  .limit(20)




Cleanup (OpenTelemetry Demo)

If you started the OpenTelemetry demo stack and want to stop everything:

docker compose down --volumes --remove-orphans




Notes
	•	This demo stays at the service level for clarity and reproducibility.
	•	Future extensions (out of scope for v1) could include:
	•	Span-level graphs
	•	Critical path analysis
	•	Trace-as-graph modeling
