// ============================================================================
// UNDERWRITING  -  a risk-screening view for one applicant.
// Not an approve/decline decision: the dataset has no verified income or full
// credit history. This surfaces risk signals for a human reviewer.
//
// Three angles, all off one account:
//   1. Own credit      : loan amount and status
//   2. Liquidity       : balance behaviour vs recurring commitments
//   3. Shared exposure : who else is on the account (joint liability)
// Transactions are aggregated with WITH before later branches to avoid fan-out.
// ============================================================================

MATCH (client:Client)-[:HAS_DISPOSITION]->(disp:Disposition)-[:FOR_ACCOUNT]->(account:Account)
WHERE disp.role = 'OWNER' AND client.name = 'Pavel Doležal'

OPTIONAL MATCH (account)-[:HAS_LOAN]->(loan:Loan)
OPTIONAL MATCH (client)-[:LIVES_IN]->(district:District)

OPTIONAL MATCH (account)-[:HAS_TRANSACTION]->(txn:Transaction)
WITH client, account, loan, district,
     count(txn)        AS txn_count,
     min(txn.balance)  AS min_balance,
     avg(txn.balance)  AS avg_balance

OPTIONAL MATCH (account)-[:HAS_ORDER]->(order:Order)
WITH client, account, loan, district, txn_count, min_balance, avg_balance,
     sum(order.amount)                      AS standing_order_total,
     count(order)                           AS standing_order_count,
     collect(DISTINCT order.order_category) AS standing_order_categories

OPTIONAL MATCH (account)<-[:FOR_ACCOUNT]-(:Disposition)<-[:HAS_DISPOSITION]-(coOwner:Client)
WHERE coOwner <> client
WITH client, account, loan, district,
     txn_count, min_balance, avg_balance,
     standing_order_total, standing_order_count, standing_order_categories,
     collect(DISTINCT coOwner.name) AS shared_account_holders

RETURN
  client.name             AS client_name,
  loan.amount             AS loan_amount,
  loan.loan_status        AS loan_status,
  txn_count,
  avg_balance,
  min_balance,
  standing_order_total,
  standing_order_count,
  standing_order_categories,
  shared_account_holders,
  district.district_name  AS district,
  district.avg_salary     AS district_avg_salary
