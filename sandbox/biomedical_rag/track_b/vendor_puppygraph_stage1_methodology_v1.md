# Methodology Summary — Stage 1 Track B (MultiHop RAG)

Vendor: **puppygraph**

## Pipeline architecture

```
MultiHopRAG corpus (609 news articles)
        │
        ├── build_graph.py ───────────────► metadata layer (no LLM)
        │      Article, Source, Author, Category nodes
        │      PUBLISHED_BY / WRITTEN_BY / IN_CATEGORY edges
        │
        └── cocoindex_flow.py (LLM) ──────► entity layer
               Organization / Person / Product / Event / Location nodes
               MENTIONS (Article→Entity), RELATED (Entity→Entity) edges
        │
        ▼
   PostgreSQL  (nodes + edges as relational tables)
        │
        ▼
   PuppyGraph  (zero-ETL graph over Postgres; Gremlin + Cypher)
        │
        ▼
   answer_questions.py  (GraphRAG: retrieve subgraph → reason → cite)
        │
        ▼
   Section 8 artifacts (graph JSONL + manifest, Q&A, traces, metrics)
```

## Models and versions

- **Graph construction (entity layer):** [cocoindex](https://cocoindex.io) 0.3.39 flow
  with an OpenAI-compatible LLM (`COCOINDEX_LLM_MODEL` / `COCOINDEX_LLM_ADDRESS`; local
  Ollama also works). Two models were run over the full corpus and both graphs saved
  under `output/by-model/`: `gpt-4o-mini` (fast/cheap baseline) and `gpt-5-mini`
  (≈2× entities, ≈2.5× relationships; the canonical submitted graph). The metadata
  layer uses no model — it is a deterministic projection of article metadata.
- **Retrieval & answering:** OpenAI-compatible chat model (`MHRAG_LLM_MODEL`; the
  measured run used `gpt-5-mini`) over subgraphs retrieved from PuppyGraph via Cypher.
  The multi-hop step is graph-native: a 4-hop outlet-intersection Cypher query finds
  the entities mentioned by both named outlets' coverage, and the LLM selects and
  verifies the answer against the article-level context.
- **Graph engine:** PuppyGraph `1.1.0` over PostgreSQL `15.15` (pinned; recorded in the build-info artifact).

## Ontologies

The MultiHop RAG data is non-clinical news, so no clinical vocabularies (SNOMED CT /
RxNorm / LOINC) apply. The graph uses a fixed two-level ontology:

- **Vertex labels:** Article (with Datetime `published_at`), Source, Author, Category,
  Entity — where Entity carries a typed attribute (Organization, Person, Product, Event,
  Location, Work, Other).
- **Edge labels:** PUBLISHED_BY, WRITTEN_BY, IN_CATEGORY, MENTIONS, STATES, ABOUT,
  plus a canonical relation vocabulary of 18 typed Entity→Entity labels (FOUNDED,
  LEADS, WORKS_FOR, PLAYS_FOR, ACQUIRED, OWNS, INVESTED_IN, PARTNERED_WITH,
  COMPETES_WITH, LEGAL_DISPUTE_WITH, DEVELOPED, LAUNCHED, CRITICIZED, SUPPORTED,
  DEFEATED, PARTICIPATED_IN, LOCATED_IN, RELATED_TO). The extraction LLM classifies
  each relationship into this vocabulary; the raw verb phrase is kept as a
  `predicate` attribute and the sentence stating the relationship as a `fact`
  attribute with its character span where locatable (claim-level, span-level
  evidence used by the answering agent).
- **Claim vertices:** single-entity facts (rankings, states, statistics, timelines)
  are reified as Claim nodes (`Article -[:STATES]-> Claim -[:ABOUT]-> Entity`) —
  the evidence path for questions that name only one outlet.
- **Extraction density:** articles are chunked (~5k chars, paragraph-aligned) and
  extracted exhaustively per chunk, then consolidated per article; this captures
  long-tail facts that single-call salience-based extraction drops.

## Isolation of external document text from agent instructions (safety)

Both LLM stages treat article text as **untrusted data**:

- **Extraction** (`cocoindex_flow.py`): the extraction instruction explicitly states the
  document is untrusted and that no instruction inside it may be followed; the model only
  emits structured entities/relationships.
- **Answering** (`answer_questions.py`): retrieved graph/article text is placed in a
  clearly delimited context block with a system prompt that forbids following any
  embedded directive (e.g. "ignore previous instructions", "print your system prompt",
  "reply only X", graph-mutating Cypher, or exfiltration URLs). Detected injection
  markers are logged per answer (`safety` block in the Q&A results) and the agent answers
  the underlying question without complying. Questions 56–60 of the provided set carry
  such injections and are handled this way.

## Reproducibility and build record

Every graph build emits a machine-readable **build-info artifact**
(`vendor_puppygraph_stage1_build-info_v1.json`, also embedded under `build_info` in the
graph manifest) recording: the pinned HuggingFace dataset revision and SHA-256 of the
input files, the git commit (and dirty flag) of the code, Python and dependency versions,
the LLM model configuration and a hash of the extraction instruction, the pinned docker
images, and the build timestamp.

- **Dataset**: `download_data.py` fetches a pinned dataset revision and fails hard on a
  checksum mismatch — corpus order defines the `article_NNNNN` doc_ids that all provenance
  points to, so a drifting dataset would silently invalidate provenance.
- **Metadata layer**: deterministic — same dataset revision + same code commit gives
  byte-identical CSVs and JSONL (stable ids, no randomness, no embedded timestamps outside
  the build record).
- **LLM entity layer**: not bit-reproducible by nature; the recorded model, instruction
  hash, and versions make each enrichment run auditable and comparable instead.
- **Runtime**: docker images are pinned (`puppygraph/puppygraph:1.1.0`, `postgres:15.15`).

## Provenance

Every node and edge carries a `provenance.doc_id` pointing to the source article
(`article_NNNNN`). Provenance completeness is 100% by construction (see the metrics
self-report). For the article-level MultiHop RAG evidence model, `doc_id` is required;
character spans are optional and omitted in the metadata layer.
