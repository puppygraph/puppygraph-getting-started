# OpenTelemetry Service Dependency Graph Demo

## Summary

This demo showcases how to map and analyze the dependencies between microservices using PuppyGraph's graph querying capabilities, running directly over PostgreSQL tables with no ETL required.
In a microservices system, a slow or failing service affects every service that calls it, directly or through a chain of other services. PuppyGraph turns those chains into paths in a graph, so you can find everything that depends on a service, see how far an outage would spread, and spot where latency builds up.

By modeling service-to-service calls as a graph, we can easily analyze:

- Upstream and downstream service dependencies
- High-traffic service interactions
- Potential latency bottlenecks across microservices

The data is a pre-built snapshot of traces from the [OpenTelemetry Demo](https://github.com/open-telemetry/opentelemetry-demo), a sample microservices web shop maintained by the OpenTelemetry project, aggregated into one row per service and one row per service-to-service call.
This demo uses PostgreSQL to store the snapshot.

**Overview:**

- **`docker-compose.yaml`**: Defines the docker services needed to run the demo. This includes both the PostgreSQL database and the PuppyGraph instance.
- **`data/`**: Contains the trace snapshot as CSV files. `services.csv` lists the services, and `service_edges.csv` lists which service calls which, with the number of calls (`call_count`) and their average latency in milliseconds (`avg_latency_ms`). The PostgreSQL setup script is located at `data/init.sql`.
- **`schema.json`**: Maps each service to a `Service` vertex and each service-to-service call to a `CALLS` edge.

## Prerequisites:

- Docker
- An API key for an AI model provider (optional), to ask questions in natural language with PuppyGraph AI. See the [PuppyGraph AI documentation](https://docs.puppygraph.com/ai/puppygraph-ai/) for supported providers.

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

PostgreSQL loads the CSV files from `data/` the first time it starts.

## Modeling the Graph

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:

- Username: `puppygraph`
- Password: `puppygraph123`

2. Upload the schema:

- On the **Upload Schema** card, click **Upload JSON**, then **Select Schema File**, choose `schema.json` and click **Upload**.
- Alternatively, you can upload the schema via the following command:

```bash
curl -XPOST -H "content-type: application/json" --data-binary @./schema.json --user "puppygraph:puppygraph123" localhost:8081/schema
```

## Querying the Graph

You can query the graph in two ways: ask questions in natural language with PuppyGraph AI, or write Cypher yourself in the Query panel.

### Using PuppyGraph AI

PuppyGraph AI is a built-in chatbot that turns natural language questions into Cypher, runs them over the graph, and shows the generated query along with the results.

1. Click **AI** in the left panel.
2. The first time, enter your API key and click **Save & Continue**. You can update the key later in **Settings**. PuppyGraph AI uses Anthropic's Claude models by default; to use an OpenAI-style API or your own model endpoint, see the [PuppyGraph AI documentation](https://docs.puppygraph.com/ai/puppygraph-ai/).
3. Ask a question about the services, for example:

- "What data do I have?"
- "Which services depend on product-catalog, directly or through other services?"
- "What are the slowest service-to-service calls?"

### Using the Query Panel

To run the example Cypher queries below yourself, navigate to the Query panel on the left side and select **Cypher**. Queries that return a path are drawn on the **Graph** tab; queries that return columns appear on the **Table** tab.

After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization.
You can do this by clicking the **Clear Canvas** button located in the top-right corner of the page.

Example Queries:

1. Show the full service dependency graph

```cypher
MATCH p = (:Service)-[:CALLS]->(:Service)
RETURN p
```

2. Find all services that depend on `product-catalog`, directly or through other services, and would be affected if it went down

```cypher
MATCH p = (:Service)-[:CALLS*1..5]->(:Service {service_name: 'product-catalog'})
RETURN p
```

3. Find the five slowest service-to-service calls. The filter skips calls averaging a minute or more: in this data those are `flagd` streaming connections that stay open until they time out, not slow requests.

```cypher
MATCH p = (:Service)-[r:CALLS]->(:Service)
WHERE r.avg_latency_ms < 60000
RETURN p
ORDER BY r.avg_latency_ms DESC
LIMIT 5
```

4. Show the same five calls as a table, with call volume alongside latency

```cypher
MATCH (a:Service)-[r:CALLS]->(b:Service)
WHERE r.avg_latency_ms < 60000
RETURN a.service_name AS caller, b.service_name AS callee,
       r.call_count AS calls, r.avg_latency_ms AS avg_latency_ms
ORDER BY avg_latency_ms DESC
LIMIT 5
```

## Cleanup and Teardown

- To stop and remove the containers and the loaded data, run:

```bash
docker compose down -v
```
