# Stage 1 Track A metrics self-report

Authoritative version: v2
Execution environment: live PuppyGraph run

| Domain | Metric | Result | Configuration |
| --- | --- | --- | --- |
| Retrieval and reasoning | Answer and citation quality | Not self-scored; Cotiviti scores against its withheld key | PrimeKG Dataverse v2.1 |
| Reported NFRs | Query latency p50 / p95 / p99 | 286 / 6613 / 61774 ms over 95 successful queries | PuppyGraph 1.1.0, 16 logical CPUs / 62.1 GiB, concurrency 1; external zero-ETL — every hop pushed down to PostgreSQL. Local-table mirroring is available and much faster, but its lean projection omits the wide narrative columns questions 68, 70 and 75 read, so the submitted capture is taken entirely in external mode |
| Reported NFRs | Cost | $0.0408 for the 95-query suite ($0.000429 per query) | No model inference: the Track A path is deterministic Cypher, so the only cost is compute. Derived from 191 s of measured query time at $0.768/hour for the measured host (16 vCPU / 62.1 GiB). Excludes the one-off dataset download and PostgreSQL import, and any standing cost of keeping the instance available between queries. |

Graph construction, provenance-completeness scoring for a constructed graph, and
ingestion-throughput rows are omitted because they do not apply to Track A: PrimeKG
is a provided graph, so the vendor does not build or ingest it.
