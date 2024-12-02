DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS accountrepayloan;
DROP TABLE IF EXISTS accounttransferaccount;
DROP TABLE IF EXISTS accountwithdrawaccount;
DROP TABLE IF EXISTS company;
DROP TABLE IF EXISTS companyapplyloan;
DROP TABLE IF EXISTS companyguaranteecompany;
DROP TABLE IF EXISTS companyinvestcompany;
DROP TABLE IF EXISTS companyownaccount;
DROP TABLE IF EXISTS loan;
DROP TABLE IF EXISTS loandepositaccount;
DROP TABLE IF EXISTS medium;
DROP TABLE IF EXISTS mediumsigninaccount;
DROP TABLE IF EXISTS person;
DROP TABLE IF EXISTS personapplyloan;
DROP TABLE IF EXISTS personguaranteeperson;
DROP TABLE IF EXISTS personinvestcompany;
DROP TABLE IF EXISTS personownaccount;

CREATE TABLE IF NOT EXISTS account
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_Account';

CREATE TABLE IF NOT EXISTS accountrepayloan
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_AccountRepayLoan';

CREATE TABLE IF NOT EXISTS accounttransferaccount
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_AccountTransferAccount';

CREATE TABLE IF NOT EXISTS accountwithdrawaccount
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_AccountWithdrawAccount';

CREATE TABLE IF NOT EXISTS company
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_Company';

CREATE TABLE IF NOT EXISTS companyapplyloan
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_CompanyApplyLoan';

CREATE TABLE IF NOT EXISTS companyguaranteecompany
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_CompanyGuaranteeCompany';

CREATE TABLE IF NOT EXISTS companyinvestcompany
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_CompanyInvestCompany';

CREATE TABLE IF NOT EXISTS companyownaccount
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_CompanyOwnAccount';

CREATE TABLE IF NOT EXISTS loan
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_Loan';

CREATE TABLE IF NOT EXISTS loandepositaccount
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_LoanDepositAccount';

CREATE TABLE IF NOT EXISTS medium
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_Medium';

CREATE TABLE IF NOT EXISTS mediumsigninaccount
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_MediumSignInAccount';

CREATE TABLE IF NOT EXISTS person
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_Person';

CREATE TABLE IF NOT EXISTS personapplyloan
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_PersonApplyLoan';

CREATE TABLE IF NOT EXISTS personguaranteeperson
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_PersonGuaranteePerson';

CREATE TABLE IF NOT EXISTS personinvestcompany
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_PersonInvestCompany';

CREATE TABLE IF NOT EXISTS personownaccount
USING DELTA
LOCATION '<s3 URI for the compaction>/public/default/pg_PersonOwnAccount';

