# Operations Report — Stage 1 Track B (MultiHop RAG)

Vendor: **puppygraph**

Non-functional numbers depend on the machine, model, and concurrency that produced
them; those must be stated alongside any figure to be comparable. Ingestion numbers
below are **measured** on the configuration stated. Query-latency and cost rows not
yet measured are marked _to be measured_. The metadata-only graph build is
deterministic and LLM-free; the entity layer and answering costs scale with the LLM.

## Configuration (state exactly what was used)

| Item | Value |
|---|---|
| Machine type / vCPU / RAM | AWS Linux host, 16 vCPU, 62 GB RAM (kernel 6.8.0-1060-aws) |
| GPU | none |
| Graph engine | PuppyGraph `1.1.0` (pinned) |
| Backing store | PostgreSQL `15.15` (pinned) |
| Extraction LLM | OpenAI API: `gpt-5-mini` (dense chunked extraction) |
| Answering LLM | `gpt-5-mini` (measured run; `MHRAG_LLM_MODEL` to override) |
| Concurrency | cocoindex 0.3.39 defaults (async row-level parallelism) |

## Ingestion throughput (graph build) — measured

| Stage | Metric | Value |
|---|---|---|
| Metadata layer (`build_graph.py`) | 609 articles → graph | ~2 s (LLM-free, deterministic) |
| Entity layer (`gpt-5-mini`, dense chunked extraction) | 609 articles, full extraction | ~60 min ≈ 0.17 articles/s |
| | documents / day (sustained, extrapolated) | ~15,000 |
| Incremental re-ingestion (amended/added articles only) | per article | ~6 s |

The submitted graph: 59,940 nodes (including 30,504 Claim vertices for
single-entity facts, ~97% with character spans), 147,002 edges (43,966 MENTIONS,
40,269 typed relations each carrying its supporting fact sentence), 609/609
documents covered, zero row errors on the final run. Extraction is chunked
(~5k-char, paragraph-aligned) and exhaustive; throughput scales linearly with
LLM concurrency, so the sustained figure reflects this single-host default
configuration, not a ceiling.

## Query latency (answering the 60-question set) — measured

| Percentile | Latency (ms) | Queries measured |
|---|---|---|
| p50 | 9,539 | 60 |
| p95 | 20,615 | 60 |
| p99 | 32,390 | 60 |

Latency is wall-clock from question-in to answer-out, including PuppyGraph retrieval
(the 4-hop outlet-intersection Cypher plus article context) and `gpt-5-mini` reasoning;
the LLM dominates. All 60 questions of the provided set are answered; answer and
citation quality are scored by Cotiviti against the withheld answer key and are
not self-reported (per Section 8.4). Safety behavior: all 5 prompt-injection
probes (questions 56-60) were handled without complying — no graph mutation, no
tool/URL calls, no system-prompt disclosure — and an empty-retrieval guard
abstains deterministically rather than letting the model answer without
evidence.

## Cost

Pricing basis: OpenAI list prices at time of run — `gpt-5-mini` $0.25 per 1M input
tokens / $2.00 per 1M output tokens (output includes reasoning tokens).
Token volumes are estimated from corpus size
(~6.8 MB ≈ 1.7M body tokens; chunked exhaustive extraction re-sends headers and
instruction per chunk, ~3M input tokens total) and observed output density.
Figures are estimates, not metered billing.

| Item | Basis | Estimate |
|---|---|---|
| Graph build by document ingestion (`gpt-5-mini`, dense chunked extraction, 609 articles — the submitted graph) | ~3M input + ~5M output tokens incl. reasoning | ≈ $11–15 total ≈ $0.02–0.025 / article |
| Metadata layer (`build_graph.py`) | no LLM | $0 |
| Query answering (`gpt-5-mini`, 60 questions) | ~6k input + ~1.5k output tokens per question | ≈ $0.01 / question ≈ $0.60 / full set |
| End-to-end submission run (ingestion + answers) | sum of the above | ≈ $12–16 |

Compute/storage cost is negligible at this corpus size (single host, ~1 h wall
clock, tens of MB of storage).

## Incremental update

cocoindex tracks source state and re-processes only changed/added articles, so an amended
record does not require full re-ingestion. PuppyGraph reads the Postgres tables live, so
no separate graph re-load is needed after the tables change.
