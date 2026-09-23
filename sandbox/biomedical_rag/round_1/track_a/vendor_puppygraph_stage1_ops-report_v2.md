# Stage 1 Track A operations report

Authoritative version: v2
Execution environment: live PuppyGraph run

- Dataset: PrimeKG Dataverse v2.1, loaded as a provided graph
- Graph engine: PuppyGraph 1.1.0
- Query protocol: PuppyGraph `/submitCypher`
- Serving mode: external zero-ETL — every hop pushed down to PostgreSQL. Local-table mirroring is available and much faster, but its lean projection omits the wide narrative columns questions 68, 70 and 75 read, so the submitted capture is taken entirely in external mode
- Concurrency: 1
- Host: Linux-6.8.0-1060-aws-x86_64-with-glibc2.35
- CPU allocation detected: 16 logical CPUs
- Memory detected: 62.1 GiB
- Queries measured: 95
- Latency p50 / p95 / p99: 286 / 6613 / 61774 ms over 95 successful queries
- Incremental graph update: not applicable; Track A uses the provided frozen graph
- Cost: $0.0408 for the 95-query suite ($0.000429 per query)
- Cost basis: No model inference: the Track A path is deterministic Cypher, so the only cost is compute. Derived from 191 s of measured query time at $0.768/hour for the measured host (16 vCPU / 62.1 GiB). Excludes the one-off dataset download and PostgreSQL import, and any standing cost of keeping the instance available between queries.
