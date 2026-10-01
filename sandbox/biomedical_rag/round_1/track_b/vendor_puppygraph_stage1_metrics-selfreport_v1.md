# Metrics Self-Report — Stage 1 Track B (MultiHop RAG)

Vendor: **puppygraph** · Dataset: **multihop_rag** · Schema version: **graph-1.0**

Computed by `metrics_report.py` directly from the submitted graph-nodes / graph-edges files. Clinical-context accuracy does not apply (non-clinical data). Accuracy rows that need a gold reference graph (entity-extraction F1, entity linking, relation-extraction F1) are not reported — no reference graph is supplied.

| Domain | Metric | Value | Applies to |
|---|---|---|---|
| Graph construction | Schema conformance (gating) — violations / 1,000 elements | **0.0** | Track B |
| Graph construction | Provenance completeness (gating) — nodes with doc_id | **100.0%** | Track B |
| Graph construction | Provenance completeness (gating) — edges with doc_id | **100.0%** | Track B |
| Graph construction | Coverage — source documents represented by ≥1 edge | **100.0%** | Track B |
| Graph construction | Connectivity — orphan-node rate | **0.0%** | Track B |
| Retrieval & reasoning | Answer & citation quality | scored by Cotiviti (withheld key) | All |
| Reported NFR | Ingestion throughput (with config) | see ops-report.md | Track B |
| Reported NFR | Query latency p50/p95/p99 (with config) | see ops-report.md | All |
| Reported NFR | Cost per document (with config) | see ops-report.md | All |

**Graph size.** 59,940 nodes, 147,002 edges, 609 source documents.

**Node counts by type**

| Type | Count |
|---|---|
| Claim | 30,313 |
| Other | 7,903 |
| Person | 7,696 |
| Organization | 4,693 |
| Product | 2,983 |
| Work | 2,238 |
| Event | 1,780 |
| Location | 1,372 |
| Article | 609 |
| Author | 298 |
| Source | 49 |
| Category | 6 |

**Edge counts by type**

| Predicate | Count |
|---|---|
| MENTIONS | 43,966 |
| STATES | 30,504 |
| ABOUT | 30,504 |
| RELATED_TO | 22,273 |
| PLAYS_FOR | 3,620 |
| PARTICIPATED_IN | 2,346 |
| LOCATED_IN | 2,013 |
| WORKS_FOR | 1,838 |
| COMPETES_WITH | 1,499 |
| LEADS | 1,008 |
| DEVELOPED | 996 |
| DEFEATED | 889 |
| PUBLISHED_BY | 609 |
| IN_CATEGORY | 609 |
| LAUNCHED | 599 |
| OWNS | 580 |
| PARTNERED_WITH | 568 |
| SUPPORTED | 549 |
| WRITTEN_BY | 541 |
| CRITICIZED | 399 |
| INVESTED_IN | 347 |
| ACQUIRED | 299 |
| FOUNDED | 235 |
| LEGAL_DISPUTE_WITH | 211 |

