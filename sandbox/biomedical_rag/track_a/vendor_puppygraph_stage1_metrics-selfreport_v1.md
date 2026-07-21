# Stage 1 Track A metrics self-report

Authoritative version: v1
Execution environment: live PuppyGraph run

| Domain | Metric | Result | Configuration |
| --- | --- | --- | --- |
| Retrieval and reasoning | Answer and citation quality | Not self-scored; Cotiviti scores against its withheld key | PrimeKG Dataverse v2.1 |
| Reported NFRs | Query latency p50 / p95 / p99 | 286 / 2198 / 4542 ms over 95 successful queries | PuppyGraph 1.1.0, 16 logical CPUs / 61.4 GiB, concurrency 1; external zero-ETL by default; the join-heavy tail (Q39/Q42/Q44) served from PuppyGraph local tables (slow3 preset: 5 node + 5 edge labels, 170,324 rows) |
| Reported NFRs | Cost | Not separately metered; deterministic read-only Cypher on self-hosted PuppyGraph (no per-query model/API spend) | Self-hosted single-node local POC on a 16 vCPU / 61 GiB host; provide production deployment pricing before final submission |

Graph construction, provenance-completeness scoring for a constructed graph, and
ingestion-throughput rows are omitted because they do not apply to Track A: PrimeKG
is a provided graph, so the vendor does not build or ingest it.
