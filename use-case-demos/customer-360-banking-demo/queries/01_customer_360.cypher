// ============================================================================
// CUSTOMER 360  -  everything about one customer in a single traversal.
// Two versions below: TABLE (verify the numbers) and VISUAL (the graph picture).
// ============================================================================


// ----------------------------------------------------------------------------
// TABLE version: returns columns. Run in table / result mode.
// Transactions are aggregated with WITH before other branches so the co-owner
// branch cannot inflate the transaction count.
// ----------------------------------------------------------------------------
MATCH (client:Client)-[:HAS_DISPOSITION]->(disp:Disposition)-[:FOR_ACCOUNT]->(account:Account)
WHERE client.name = 'Pavel Doležal' AND disp.role = 'OWNER'

OPTIONAL MATCH (account)-[:HAS_TRANSACTION]->(txn:Transaction)
WITH client, disp, account,
     count(txn)        AS txn_count,
     avg(txn.amount)   AS avg_txn_amount,
     max(txn.balance)  AS max_balance

OPTIONAL MATCH (account)-[:HAS_LOAN]->(loan:Loan)
OPTIONAL MATCH (disp)-[:HAS_CARD]->(card:Card)
OPTIONAL MATCH (account)-[:HAS_ORDER]->(order:Order)
WITH client, disp, account, txn_count, avg_txn_amount, max_balance, loan, card,
     collect(order.amount) AS standing_order_amounts

OPTIONAL MATCH (client)-[:LIVES_IN]->(district:District)
OPTIONAL MATCH (account)<-[:FOR_ACCOUNT]-(:Disposition)<-[:HAS_DISPOSITION]-(coOwner:Client)
WHERE coOwner <> client
WITH client, disp, account, txn_count, avg_txn_amount, max_balance, loan, card,
     standing_order_amounts, district, collect(DISTINCT coOwner.name) AS co_owners

RETURN
  client.name             AS client_name,
  district.district_name  AS district,
  district.avg_salary     AS district_avg_salary,
  id(account)             AS account_id,
  disp.role               AS role,
  txn_count,
  avg_txn_amount,
  max_balance,
  loan.amount             AS loan_amount,
  loan.loan_status        AS loan_status,
  card.card_type          AS card_type,
  standing_order_amounts,
  co_owners


// ----------------------------------------------------------------------------
// VISUAL version: returns nodes AND named relationships. Run in graph mode.
// Returning the relationships is what makes the canvas draw edges (nodes alone
// render as disconnected dots). Transactions are intentionally excluded here:
// 600+ transaction nodes would make the graph unreadable.
// ----------------------------------------------------------------------------
MATCH (client:Client)-[hasDisp:HAS_DISPOSITION]->(disp:Disposition)-[forAccount:FOR_ACCOUNT]->(account:Account)
WHERE client.name = 'Pavel Doležal' AND disp.role = 'OWNER'
OPTIONAL MATCH (account)-[hasLoan:HAS_LOAN]->(loan:Loan)
OPTIONAL MATCH (disp)-[hasCard:HAS_CARD]->(card:Card)
OPTIONAL MATCH (client)-[livesIn:LIVES_IN]->(district:District)
OPTIONAL MATCH (account)-[hasOrder:HAS_ORDER]->(order:Order)
OPTIONAL MATCH (account)<-[forAccount2:FOR_ACCOUNT]-(coDisp:Disposition)<-[hasDisp2:HAS_DISPOSITION]-(coOwner:Client)
WHERE coOwner <> client
RETURN client, hasDisp, disp, forAccount, account,
       hasLoan, loan, hasCard, card, livesIn, district,
       hasOrder, order, forAccount2, coDisp, hasDisp2, coOwner
