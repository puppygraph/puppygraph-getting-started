-- 1. Account
DROP MATERIALIZED VIEW IF EXISTS account_mv;
DROP SOURCE IF EXISTS account_stream CASCADE;

-- 2. AccountRepayLoan
DROP MATERIALIZED VIEW IF EXISTS accountrepayloan_mv;
DROP SOURCE IF EXISTS accountrepayloan_stream CASCADE;

-- 3. AccountTransferAccount
DROP MATERIALIZED VIEW IF EXISTS accounttransferaccount_mv;
DROP SOURCE IF EXISTS accounttransferaccount_stream CASCADE;

-- 4. AccountWithdrawAccount
DROP MATERIALIZED VIEW IF EXISTS accountwithdrawaccount_mv;
DROP SOURCE IF EXISTS accountwithdrawaccount_stream CASCADE;

-- 5. Company
DROP MATERIALIZED VIEW IF EXISTS company_mv;
DROP SOURCE IF EXISTS company_stream CASCADE;

-- 6. CompanyApplyLoan
DROP MATERIALIZED VIEW IF EXISTS companyapplyloan_mv;
DROP SOURCE IF EXISTS companyapplyloan_stream CASCADE;

-- 7. CompanyGuaranteeCompany
DROP MATERIALIZED VIEW IF EXISTS companyguaranteecompany_mv;
DROP SOURCE IF EXISTS companyguaranteecompany_stream CASCADE;

-- 8. CompanyInvestCompany
DROP MATERIALIZED VIEW IF EXISTS companyinvestcompany_mv;
DROP SOURCE IF EXISTS companyinvestcompany_stream CASCADE;

-- 9. CompanyOwnAccount
DROP MATERIALIZED VIEW IF EXISTS companyownaccount_mv;
DROP SOURCE IF EXISTS companyownaccount_stream CASCADE;

-- 10. Loan
DROP MATERIALIZED VIEW IF EXISTS loan_mv;
DROP SOURCE IF EXISTS loan_stream CASCADE;

-- 11. LoanDepositAccount
DROP MATERIALIZED VIEW IF EXISTS loandepositaccount_mv;
DROP SOURCE IF EXISTS loandepositaccount_stream CASCADE;

-- 12. Medium
DROP MATERIALIZED VIEW IF EXISTS medium_mv;
DROP SOURCE IF EXISTS medium_stream CASCADE;

-- 13. MediumSignInAccount
DROP MATERIALIZED VIEW IF EXISTS mediumsigninaccount_mv;
DROP SOURCE IF EXISTS mediumsigninaccount_stream CASCADE;

-- 14. Person
DROP MATERIALIZED VIEW IF EXISTS person_mv;
DROP SOURCE IF EXISTS person_stream CASCADE;

-- 15. PersonApplyLoan
DROP MATERIALIZED VIEW IF EXISTS personapplyloan_mv;
DROP SOURCE IF EXISTS personapplyloan_stream CASCADE;

-- 16. PersonGuaranteePerson
DROP MATERIALIZED VIEW IF EXISTS personguaranteeperson_mv;
DROP SOURCE IF EXISTS personguaranteeperson_stream CASCADE;

-- 17. PersonInvestCompany
DROP MATERIALIZED VIEW IF EXISTS personinvestcompany_mv;
DROP SOURCE IF EXISTS personinvestcompany_stream CASCADE;

-- 18. PersonOwnAccount
DROP MATERIALIZED VIEW IF EXISTS personownaccount_mv;
DROP SOURCE IF EXISTS personownaccount_stream CASCADE;
