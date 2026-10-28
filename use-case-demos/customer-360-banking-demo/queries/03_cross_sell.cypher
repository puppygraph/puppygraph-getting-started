// ============================================================================
// CROSS-SELL  -  find the best candidates to offer a credit card.
// The idea: find what is ABSENT. Reach for a card, keep only owners who have
// none, then rank the cardless owners by financial health and activity.
// Money leads (avg_balance), activity is the tiebreak (txn_count).
// ============================================================================

MATCH (client:Client)-[:HAS_DISPOSITION]->(disp:Disposition)-[:FOR_ACCOUNT]->(account:Account)
WHERE disp.role = 'OWNER'

// Absence filter: reach for a card, keep only the owners with none.
OPTIONAL MATCH (disp)-[:HAS_CARD]->(card:Card)
WITH client, account, card
WHERE card IS NULL

// Signal: engagement and financial health.
OPTIONAL MATCH (account)-[:HAS_TRANSACTION]->(txn:Transaction)
WITH client, account,
     count(txn)       AS txn_count,
     avg(txn.balance) AS avg_balance

RETURN
  client.name   AS client_name,
  id(account)   AS account_id,
  avg_balance,
  txn_count
ORDER BY avg_balance DESC, txn_count DESC
LIMIT 15
