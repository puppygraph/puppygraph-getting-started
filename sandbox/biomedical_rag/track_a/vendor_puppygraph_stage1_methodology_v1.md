# Stage 1 Track A methodology summary

Authoritative version: v1

PrimeKG Dataverse v2.1 is checksum-pinned, loaded into PostgreSQL, and exposed
through PuppyGraph 1.1.0. Each precise Cotiviti question has a separately versioned
Cypher translation. The runner statically rejects mutation, procedure, and external
load tokens before submitting a statement. Answers are projected from the returned
records; stable PrimeKG node references are resolved from `nodes.csv`, and the exact
raw query result is retained as an auditable source record.

Question and graph text are always treated as untrusted data. Embedded instructions
cannot change the execution policy, request graph mutation, trigger external export,
or replace graph retrieval. This is exercised explicitly by questions 96–100.

No generative model or external ontology is used in this deterministic Track A path.
