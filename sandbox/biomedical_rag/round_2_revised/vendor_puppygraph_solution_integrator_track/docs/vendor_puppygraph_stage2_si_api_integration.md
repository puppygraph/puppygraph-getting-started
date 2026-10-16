# PuppyGraph — Integration API Surface (SI Track, Cotiviti CCV POC)

Sep 22, 2026 · PuppyGraph + Quark Labs

## Submission declaration

| Field | Value |
| --- | --- |
| Vendor name | PuppyGraph (retrieval layer), with Quark Labs (data preparation) |
| Vendor track | Solution Integrator |
| Opt-in declaration | I am opting into the Solution Integrator track |
| Integration targets | MCP-compatible agent frameworks; Java, Python, Go and JavaScript client drivers; CSV, Parquet, Iceberg and Hive exports (see INTEGRATION\_API\_SURFACE.md) |
| Submission round | Round 2 (Blind)  |

Any downstream reasoning agent can reach the PuppyGraph context layer in three ways. It can call PuppyGraph as tools over MCP, query it directly with the Java, Python, Go or JavaScript client drivers, or consume exported results as CSV, Parquet, or Iceberg and Hive tables. All three use the same standard query languages, openCypher and Gremlin, so the layer does not depend on any particular LLM or agent framework.

Context is handed off as query result rows. Each row carries the evidence passage, its document and page reference, and the claim and ICD-10 code it relates to, with identifiers already replaced by placeholders.

## Integration targets

| Surface | Protocol / format | Default port | Best for |
| --- | --- | --- | --- |
| PuppyGraph MCP server | MCP tools over Bolt, Gremlin WebSocket and REST | Uses the ports below | LLM agents in any MCP-compatible client or framework |
| Client drivers: Java, Python, Go, JavaScript | openCypher over Bolt; Gremlin over WebSocket | 7687 (Bolt), 8182 (Gremlin) | Custom agent APIs and orchestrators calling retrieval as code |
| REST API and Web UI | HTTP | 8081 | Schema metadata, inspection, reviewer access |
| Query result export | CSV, Parquet, Parquet Iceberg tables, Parquet Hive tables | — | Batch pipelines, evaluation, offline handoff |

Ports are PuppyGraph's defaults ([AI Integrations docs](https://docs.puppygraph.com/ai/ai-integrations/)) and can be changed at deployment. For the Section 0.1 declaration, the integration targets are: MCP-compatible agent frameworks, custom agent APIs in Java, Python, Go or JavaScript, and batch consumers of CSV, Parquet, Iceberg or Hive outputs.

## Agent integration via MCP

The open-source [PuppyGraph MCP server](https://github.com/puppygraph/puppygraph-mcp-server) lets any MCP-compatible agent call PuppyGraph as tools, with no custom glue code. It runs inside Cotiviti's environment next to PuppyGraph.

| Tool | What it does |
| --- | --- |
| `puppygraph_schema` | Returns the graph's labels, relationships and properties, so the agent knows what it can ask for |
| `puppygraph_query` | Runs an openCypher or Gremlin query and returns the result rows |
| `puppygraph_status` | Checks that the server can reach PuppyGraph |

The schema tool returns only what is mapped into the graph, so the `phi` table never appears to the agent. Connection details (Bolt URL, Gremlin URL, service-account credentials) are set through environment variables at deployment.

## Programmatic access via client drivers

A custom agent API or orchestrator can call retrieval as ordinary code using PuppyGraph's [client drivers](https://docs.puppygraph.com/user-interface/client-drivers/) for Java, Python, Go and JavaScript. Each language can use openCypher over Bolt or Gremlin over WebSocket.

- **openCypher over Bolt** works with Neo4j-compatible drivers, which many AI frameworks already support. It is the recommended default for agent tools because queries are short and easy to inspect.
- **Gremlin over WebSocket** suits applications that model traversal steps directly, such as walking from a claim to its ICD-10 codes to their supporting pages.

A minimal Python retrieval tool, following PuppyGraph's documented pattern:

```python
from neo4j import GraphDatabase

def retrieve(query: str, params: dict) -> list[dict]:
    with GraphDatabase.driver(BOLT_URL, auth=(SVC_USER, SVC_PASSWORD)) as driver:
        records, _, _ = driver.execute_query(query, params)
        return [r.data() for r in records]
```

PuppyGraph's guidance for agent tools also applies here: read-only queries only, a LIMIT on non-aggregate queries, and answers drawn only from returned rows.

## Bulk export

For batch pipelines and offline handoff, any openCypher or Gremlin query can write its results straight to storage instead of returning them to the caller ([Exporting Query Results](https://docs.puppygraph.com/querying/exporting-query-results/)). This fits Cotiviti's round-based evaluation: retrieval for a full set of claims can be exported once and consumed by any downstream system.

| Format | How it is written | Notes |
| --- | --- | --- |
| CSV files | To a registered export location | Default format |
| Parquet files | To a registered export location | Set `fileType: 'parquet'` |
| Parquet Iceberg tables | Through a schema catalog only | Experimental; needs CREATE TABLE on the target database |
| Parquet Hive tables | Through a schema catalog only | Experimental; supports Kerberized Hive |

Export destinations are Amazon S3, MinIO, Google Cloud Storage, Azure Data Lake Storage Gen2 and HDFS, all inside Cotiviti's environment. Only an administrator can register an export location, and catalog exports can be restricted to approved path prefixes, so results cannot be written anywhere Cotiviti has not approved.

## Required per-claim outputs

On the Solution Integrator track, Section 2.2 asks for these outputs end-to-end for every claim. The retrieval layer supplies its part of each.

| Output (Section 2.2, SI track) | What the retrieval layer contributes |
| --- | --- |
| Full reasoning, tool-call and trace detail | Every retrieval call logs the claim ID, the query issued and the rows returned. These are the retrieval steps within the pipeline's end-to-end trace |
| HITL escalation point and question per code | Codes whose evidence rows come back empty or with conflicting stances, as shown in the handoff above, mark where the pipeline stops for a human reviewer |
| Time to run each claim end-to-end | Retrieval time is logged per claim as one component of end-to-end time; engine metrics are also available through PuppyGraph's Prometheus monitoring |
| Cost of processing each claim | Infrastructure compute time per claim, plus tokens used on the configured model endpoint. PuppyGraph hosts no model of its own; model calls go to the endpoint Cotiviti chooses, so token cost is billed on Cotiviti's model |

Measured latency and cost figures are reported in the POC results submission, not in this document.

## Security

Every surface above reads through the same graph schema, so no integration can reach the unmapped `phi` table. Encryption, authentication and PHI handling are covered in [SECURITY PHI HANDLING](/sandbox/biomedical_rag/round_2/vendor_puppygraph_solution_integrator_track/vendor_puppygraph_stage2_si_security_phi_handling.md).
