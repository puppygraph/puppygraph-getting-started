1. End-to-end tracing of a patient's journey
```cypher
MATCH (p:Patient) WHERE id(p) = 'Patient[031]'
MATCH path = (p)-[*1..4]-(connected)
RETURN path
```

2. Full metastasis chain (see spread of cancer)
```cypher
MATCH path = (p:Patient)-[:HAD_METASTASIS]->(m:Metastasis)-[:NEXT_METASTASIS*1..4]->(m2:Metastasis)
RETURN path
```

3. Matching for patient profile
```cypher
MATCH path = (p:Patient)-[:RECEIVED_INITIAL_DIAGNOSIS]->(d:InitialDiagnosis)
MATCH path2 = (p)-[:UNDERWENT_ADJUVANT_TREATMENT]->(a:AdjuvantTreatment)
WHERE d.age_at_initial_diagnosis >= 50
AND d.age_at_initial_diagnosis <= 70
AND a.adjuvant_radiochemotherapy = 'yes'
RETURN path, path2
```