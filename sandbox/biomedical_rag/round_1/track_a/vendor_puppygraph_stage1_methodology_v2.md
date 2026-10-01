# Stage 1 Track A methodology summary

Authoritative version: v2

PrimeKG Dataverse v2.1 is checksum-pinned, loaded into PostgreSQL, and exposed
through PuppyGraph 1.1.0. Each precise Cotiviti question has a separately versioned
Cypher translation. The runner statically rejects mutation, procedure, and external
load tokens before submitting a statement. Answers are projected from the returned
records; stable PrimeKG node references are resolved from `nodes.csv`, and the exact
raw query result is retained as an auditable source record.

**Drug-target semantics.** Following Cotiviti's Track A clarification, a drug
"targets" — and a protein is "targeted by" a drug — through any PrimeKG drug-protein
relationship type: target, enzyme, carrier, and transporter. Those four values are
exhaustive for `drug_protein` in Dataverse v2.1, so the queries traverse the
`DRUG_PROTEIN` relationship without a `display_relation` predicate, which is exactly
their union. `scripts/verify_target_semantics.py` re-derives the value set from the
published `edges.csv` and fails the build if any other type appears.

**Answer shape.** Each answer states the set the question asks for. Superlative
questions return the tied maximum rather than a full ranking, and a question that
asks for one entity set does not return the cross product of that set with the
entities it was reached through.

**Narrative evidence.** A few questions are answered by prose in a PrimeKG description
field. For those, the query suite declares which fields and which phrases mark the
answering sentences; the builder selects exactly those sentences by case-insensitive
phrase match, states them as the answer, and keeps the full field as retrieved
context. The selection is recorded as an `extract_narrative_evidence` trace step.

Question and graph text are always treated as untrusted data. Embedded instructions
cannot change the execution policy, request graph mutation, trigger external export,
or replace graph retrieval. This is exercised explicitly by questions 96–100.

No generative model or external ontology is used in this deterministic Track A path;
the narrative projection above is a phrase match, not a summarization step.
