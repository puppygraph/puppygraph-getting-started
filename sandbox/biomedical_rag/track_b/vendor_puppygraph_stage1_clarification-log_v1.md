# Clarification Log — Stage 1 Track B (MultiHop RAG)

Vendor: **puppygraph**

Questions raised and the interpretation relied upon. No live Cotiviti responses were
available for this build, so each item records the assumption we proceeded on; replace
with the official response when provided at kickoff.

| # | Question | Interpretation relied upon |
|---|---|---|
| 1 | The eval doc says "57 multi-hop questions" but the dataset PDF lists 60 in Section 2. Which is authoritative? | We answer all 60 questions from the dataset PDF. Questions 56–60 embed prompt-injection probes (the safety slice); the 55 clean questions plus the injection handling cover the "57" set with margin. Every answer is flagged for injection in the `safety` block. |
| 2 | Track B provenance requires a `doc_id`; the corpus has no explicit document ids. | We assign stable ids `article_NNNNN` by corpus order and treat them as the `doc_id`. Character spans are optional at the article level and are omitted in the metadata layer. |
| 3 | Should the clinical-context block be included? | No — MultiHop RAG is non-clinical news, so `clinical_context` and `normalized_code` are omitted per Section 8.1. |
| 4 | Accuracy metrics (entity/relation F1) with no gold reference graph? | Not reported — no reference graph is supplied for MultiHop RAG. Only structural/descriptive rows (schema conformance, provenance, coverage/connectivity) are self-reported. |
| 5 | How should injected instructions in questions/nodes be handled? | Treated strictly as untrusted data. The agent never complies (no graph mutation, no tool/URL calls, no system-prompt disclosure) and answers the underlying question. Assertions a question makes about its own answerability ("this question is unanswerable") are also treated as untrusted and checked against the evidence. |
| 6 | Which submission version is authoritative? | v1 files in this package are authoritative; no earlier versions have been delivered. On any resubmission the version suffix will be incremented per Section 7.1. |
| 7 | `graph_edges_used` in the Q&A results (8.2)? | Submitted as an empty list. The reasoning traces (8.3) record the traversal steps, including the exact Cypher queries and the bridge entities they returned; per-edge ids of the traversed edges are not individually tracked by the retrieval layer. |
| 8 | Character spans (8.1, optional)? | Provided: ~97% of relationship facts and claims carry character-offset spans into the source article body. Metadata-layer nodes/edges carry doc_id-level provenance only, as permitted for article-level evidence. |
