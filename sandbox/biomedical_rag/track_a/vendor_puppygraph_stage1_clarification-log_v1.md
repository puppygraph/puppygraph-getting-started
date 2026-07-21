# Stage 1 Track A clarification log

Authoritative version: v1

| Status | Question | Current handling |
| --- | --- | --- |
| Open | For graph-native PrimeKG citations, does Cotiviti require every traversed edge instance ID, or are stable node IDs, relationship-type references, and the retained raw query-result record sufficient? | This version supplies all three references available from the PuppyGraph result path and does not invent edge-instance provenance. |
| Open | Section 8 says the `clinical_context` block (negation, uncertainty, temporality, experiencer) and the `context_check` trace step apply to clinical data. Does Cotiviti expect them for a *provided knowledge graph* like PrimeKG? | Omitted. Those fields describe patient-finding semantics in clinical records; PrimeKG's nodes and edges are curated ontology-level biomedical facts (e.g. "Drug targets Protein"), not negatable/experiencer-scoped patient observations, so the attributes are undefined here. They will apply to the Stage 2 clinical records. Requesting confirmation this is acceptable for Track A. |
| Resolved internally | Should instructions embedded in questions or retrieved node text be executed? | No. They are untrusted data; only the read-only semantic graph question is executed. |
