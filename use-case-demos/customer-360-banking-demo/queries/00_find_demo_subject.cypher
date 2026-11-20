// How we chose the demo subject.
// Rank every OWNER-account by "completeness": how many of {loan, card, co-owner}
// it has (0 to 3), then by transaction activity. Pavel Dolezal topped this list,
// so he is the customer used across all three demos.

MATCH (client:Client)-[:HAS_DISPOSITION]->(disp:Disposition)-[:FOR_ACCOUNT]->(account:Account)
WHERE disp.role = 'OWNER'

OPTIONAL MATCH (account)-[:HAS_TRANSACTION]->(txn:Transaction)
WITH client, disp, account, count(txn) AS txn_count

OPTIONAL MATCH (account)-[:HAS_LOAN]->(loan:Loan)
OPTIONAL MATCH (disp)-[:HAS_CARD]->(card:Card)
WITH client, disp, account, txn_count, loan, card

OPTIONAL MATCH (account)<-[:FOR_ACCOUNT]-(:Disposition)<-[:HAS_DISPOSITION]-(other:Client)
WHERE other <> client
WITH client, account, txn_count, loan, card, count(DISTINCT other) AS co_owner_count

WITH client, account, txn_count, co_owner_count,
     (loan IS NOT NULL) AS has_loan,
     (card IS NOT NULL) AS has_card,
     ( CASE WHEN loan IS NOT NULL   THEN 1 ELSE 0 END
     + CASE WHEN card IS NOT NULL   THEN 1 ELSE 0 END
     + CASE WHEN co_owner_count > 0 THEN 1 ELSE 0 END ) AS completeness

RETURN client.name AS client_name, id(account) AS account_id, completeness,
       has_loan, has_card, co_owner_count, txn_count
ORDER BY completeness DESC, co_owner_count DESC, txn_count DESC
LIMIT 10
