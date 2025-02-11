-- 1. Account
CREATE SOURCE IF NOT EXISTS account_stream (
  "label" varchar,
  "accountId" bigint,
  "createTime" timestamptz,
  "isBlocked" boolean,
  "accountType" varchar,
  "nickname" varchar,
  "phonenum" varchar,
  "email" varchar,
  "freqLoginType" varchar,
  "lastLoginTime" timestamptz,
  "accountLevel" varchar
)
WITH (
  connector='kafka',
  topic='kafka-Account',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 2. AccountRepayLoan
CREATE SOURCE IF NOT EXISTS accountrepayloan_stream (
  "label" varchar,
  "accountrepayloanId" bigint,
  "accountId" bigint,
  "loanId" bigint,
  "amount" double precision,
  "createTime" timestamptz
)
WITH (
  connector='kafka',
  topic='kafka-AccountRepayLoan',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 3. AccountTransferAccount
CREATE SOURCE IF NOT EXISTS accounttransferaccount_stream (
  "label" varchar,
  "accounttransferaccountId" bigint,
  "fromId" bigint,
  "toId" bigint,
  "amount" double precision,
  "createTime" timestamptz,
  "orderNum" varchar,
  "comment" varchar,
  "payType" varchar,
  "goodsType" varchar
)
WITH (
  connector='kafka',
  topic='kafka-AccountTransferAccount',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 4. AccountWithdrawAccount
CREATE SOURCE IF NOT EXISTS accountwithdrawaccount_stream (
  "label" varchar,
  "accountwithdrawaccountId" bigint,
  "fromId" bigint,
  "toId" bigint,
  "amount" double precision,
  "createTime" timestamptz
)
WITH (
  connector='kafka',
  topic='kafka-AccountWithdrawAccount',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 5. Company
CREATE SOURCE IF NOT EXISTS company_stream (
  "label" varchar,
  "companyId" bigint,
  "companyName" varchar,
  "isBlocked" boolean,
  "createTime" timestamptz,
  "country" varchar,
  "city" varchar,
  "business" varchar,
  "description" varchar,
  "url" varchar
)
WITH (
  connector='kafka',
  topic='kafka-Company',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 6. CompanyApplyLoan
CREATE SOURCE IF NOT EXISTS companyapplyloan_stream (
  "label" varchar,
  "companyapplyloanId" bigint,
  "companyId" bigint,
  "loanId" bigint,
  "createTime" timestamptz,
  "org" varchar
)
WITH (
  connector='kafka',
  topic='kafka-CompanyApplyLoan',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 7. CompanyGuaranteeCompany
CREATE SOURCE IF NOT EXISTS companyguaranteecompany_stream (
  "label" varchar,
  "companyguaranteecompanyId" bigint,
  "fromId" bigint,
  "toId" bigint,
  "createTime" timestamptz,
  "relation" varchar
)
WITH (
  connector='kafka',
  topic='kafka-CompanyGuaranteeCompany',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 8. CompanyInvestCompany
CREATE SOURCE IF NOT EXISTS companyinvestcompany_stream (
  "label" varchar,
  "companyinvestcompanyId" bigint,
  "investorId" bigint,
  "companyId" bigint,
  "ratio" real,
  "createTime" timestamptz
)
WITH (
  connector='kafka',
  topic='kafka-CompanyInvestCompany',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 9. CompanyOwnAccount
CREATE SOURCE IF NOT EXISTS companyownaccount_stream (
  "label" varchar,
  "companyownaccountId" bigint,
  "companyId" bigint,
  "accountId" bigint,
  "createTime" timestamptz
)
WITH (
  connector='kafka',
  topic='kafka-CompanyOwnAccount',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 10. Loan
CREATE SOURCE IF NOT EXISTS loan_stream (
  "label" varchar,
  "loanId" bigint,
  "loanAmount" double precision,
  "balance" double precision,
  "createTime" timestamptz,
  "loanUsage" varchar,
  "interestRate" real
)
WITH (
  connector='kafka',
  topic='kafka-Loan',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 11. LoanDepositAccount
CREATE SOURCE IF NOT EXISTS loandepositaccount_stream (
  "label" varchar,
  "loandepositaccountId" bigint,
  "loanId" bigint,
  "accountId" bigint,
  "amount" double precision,
  "createTime" timestamptz
)
WITH (
  connector='kafka',
  topic='kafka-LoanDepositAccount',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 12. Medium
CREATE SOURCE IF NOT EXISTS medium_stream (
  "label" varchar,
  "mediumId" bigint,
  "mediumType" varchar,
  "isBlocked" boolean,
  "createTime" timestamptz,
  "lastLoginTime" timestamptz,
  "riskLevel" varchar
)
WITH (
  connector='kafka',
  topic='kafka-Medium',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 13. MediumSignInAccount
CREATE SOURCE IF NOT EXISTS mediumsigninaccount_stream (
  "label" varchar,
  "mediumsigninaccountId" bigint,
  "mediumId" bigint,
  "accountId" bigint,
  "createTime" timestamptz,
  "location" varchar
)
WITH (
  connector='kafka',
  topic='kafka-MediumSignInAccount',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 14. Person
CREATE SOURCE IF NOT EXISTS person_stream (
  "label" varchar,
  "personId" bigint,
  "personName" varchar,
  "isBlocked" boolean,
  "createTime" timestamptz,
  "gender" varchar,
  "birthday" date,
  "country" varchar,
  "city" varchar
)
WITH (
  connector='kafka',
  topic='kafka-Person',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 15. PersonApplyLoan
CREATE SOURCE IF NOT EXISTS personapplyloan_stream (
  "label" varchar,
  "personapplyloanId" bigint,
  "personId" bigint,
  "loanId" bigint,
  "createTime" timestamptz,
  "org" varchar
)
WITH (
  connector='kafka',
  topic='kafka-PersonApplyLoan',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 16. PersonGuaranteePerson
CREATE SOURCE IF NOT EXISTS personguaranteeperson_stream (
  "label" varchar,
  "personguaranteepersonId" bigint,
  "fromId" bigint,
  "toId" bigint,
  "createTime" timestamptz,
  "relation" varchar
)
WITH (
  connector='kafka',
  topic='kafka-PersonGuaranteePerson',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 17. PersonInvestCompany
CREATE SOURCE IF NOT EXISTS personinvestcompany_stream (
  "label" varchar,
  "personinvestcompanyId" bigint,
  "investorId" bigint,
  "companyId" bigint,
  "ratio" real,
  "createTime" timestamptz
)
WITH (
  connector='kafka',
  topic='kafka-PersonInvestCompany',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 18. PersonOwnAccount
CREATE SOURCE IF NOT EXISTS personownaccount_stream (
  "label" varchar,
  "personownaccountId" bigint,
  "personId" bigint,
  "accountId" bigint,
  "createTime" timestamptz
)
WITH (
  connector='kafka',
  topic='kafka-PersonOwnAccount',
  properties.bootstrap.server='kafka:9092',
  scan.startup.mode='earliest'
)
FORMAT PLAIN ENCODE JSON;

-- 1. Account
CREATE MATERIALIZED VIEW IF NOT EXISTS account_mv AS
  SELECT * FROM account_stream;

-- 2. AccountRepayLoan
CREATE MATERIALIZED VIEW IF NOT EXISTS accountrepayloan_mv AS
  SELECT * FROM accountrepayloan_stream;

-- 3. AccountTransferAccount
CREATE MATERIALIZED VIEW IF NOT EXISTS accounttransferaccount_mv AS
  SELECT * FROM accounttransferaccount_stream;

-- 4. AccountWithdrawAccount
CREATE MATERIALIZED VIEW IF NOT EXISTS accountwithdrawaccount_mv AS
  SELECT * FROM accountwithdrawaccount_stream;

-- 5. Company
CREATE MATERIALIZED VIEW IF NOT EXISTS company_mv AS
  SELECT * FROM company_stream;

-- 6. CompanyApplyLoan
CREATE MATERIALIZED VIEW IF NOT EXISTS companyapplyloan_mv AS
  SELECT * FROM companyapplyloan_stream;

-- 7. CompanyGuaranteeCompany
CREATE MATERIALIZED VIEW IF NOT EXISTS companyguaranteecompany_mv AS
  SELECT * FROM companyguaranteecompany_stream;

-- 8. CompanyInvestCompany
CREATE MATERIALIZED VIEW IF NOT EXISTS companyinvestcompany_mv AS
  SELECT * FROM companyinvestcompany_stream;

-- 9. CompanyOwnAccount
CREATE MATERIALIZED VIEW IF NOT EXISTS companyownaccount_mv AS
  SELECT * FROM companyownaccount_stream;

-- 10. Loan
CREATE MATERIALIZED VIEW IF NOT EXISTS loan_mv AS
  SELECT * FROM loan_stream;

-- 11. LoanDepositAccount
CREATE MATERIALIZED VIEW IF NOT EXISTS loandepositaccount_mv AS
  SELECT * FROM loandepositaccount_stream;

-- 12. Medium
CREATE MATERIALIZED VIEW IF NOT EXISTS medium_mv AS
  SELECT * FROM medium_stream;

-- 13. MediumSignInAccount
CREATE MATERIALIZED VIEW IF NOT EXISTS mediumsigninaccount_mv AS
  SELECT * FROM mediumsigninaccount_stream;

-- 14. Person
CREATE MATERIALIZED VIEW IF NOT EXISTS person_mv AS
  SELECT * FROM person_stream;

-- 15. PersonApplyLoan
CREATE MATERIALIZED VIEW IF NOT EXISTS personapplyloan_mv AS
  SELECT * FROM personapplyloan_stream;

-- 16. PersonGuaranteePerson
CREATE MATERIALIZED VIEW IF NOT EXISTS personguaranteeperson_mv AS
  SELECT * FROM personguaranteeperson_stream;

-- 17. PersonInvestCompany
CREATE MATERIALIZED VIEW IF NOT EXISTS personinvestcompany_mv AS
  SELECT * FROM personinvestcompany_stream;

-- 18. PersonOwnAccount
CREATE MATERIALIZED VIEW IF NOT EXISTS personownaccount_mv AS
  SELECT * FROM personownaccount_stream;