# Stage 1 Track A operations report

Authoritative version: v1
Execution environment: live PuppyGraph run

- Dataset: PrimeKG Dataverse v2.1, loaded as a provided graph
- Graph engine: PuppyGraph 1.1.0
- Query protocol: PuppyGraph `/submitCypher`
- Serving mode: external zero-ETL by default; the join-heavy tail (Q39/Q42/Q44) served from PuppyGraph local tables (slow3 preset: 5 node + 5 edge labels, 170,324 rows)
- Concurrency: 1
- Host: Linux-6.8.0-1060-aws-x86_64-with-glibc2.35
- CPU allocation detected: 16 logical CPUs
- Memory detected: 61.4 GiB
- Queries measured: 95
- Latency p50 / p95 / p99: 286 / 2198 / 4542 ms over 95 successful queries
- Incremental graph update: not applicable; Track A uses the provided frozen graph
- Cost: Not separately metered; deterministic read-only Cypher on self-hosted PuppyGraph (no per-query model/API spend)
- Cost basis: Self-hosted single-node local POC on a 16 vCPU / 61 GiB host; provide production deployment pricing before final submission
