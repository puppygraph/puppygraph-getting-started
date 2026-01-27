#!/usr/bin/env bash
# Host access (from your laptop):
UC_SERVER="${UC_SERVER:-http://localhost:9000}"

CATALOG="${CATALOG:-puppygraph}"
SCHEMA="${SCHEMA:-demo}"

DELTA_BASE="${DELTA_BASE:-file:///delta/demo}"

echo "UC_SERVER=${UC_SERVER}"
echo "CATALOG=${CATALOG}"
echo "SCHEMA=${SCHEMA}"
echo "DELTA_BASE=${DELTA_BASE}"
echo

echo "== Create catalog =="
curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/catalogs" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"${CATALOG}\",\"comment\":\"created by bootstrap\"}" || true
echo

echo "== Create schema =="
curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/schemas" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"${SCHEMA}\",\"catalog_name\":\"${CATALOG}\",\"comment\":\"created by bootstrap\"}" || true
echo

echo "== Create tables (EXTERNAL DELTA) =="

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Users\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/Users\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"InternetGateways\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/InternetGateways\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"UserInternetGatewayAccess\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/UserInternetGatewayAccess\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"UserInternetGatewayAccessLog\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/UserInternetGatewayAccessLog\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"VPCs\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/VPCs\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"InternetGatewayVPC\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/InternetGatewayVPC\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Subnets\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/Subnets\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"SecurityGroups\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/SecurityGroups\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"SubnetSecurityGroup\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/SubnetSecurityGroup\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"NetworkInterfaces\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/NetworkInterfaces\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"VMInstances\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/VMInstances\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Roles\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/Roles\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Resources\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/Resources\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"RoleResourceAccess\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/RoleResourceAccess\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"PublicIPs\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/PublicIPs\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"PrivateIPs\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/PrivateIPs\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"IngressRules\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/IngressRules\"}" || true
echo

curl -i -X POST "${UC_SERVER}/api/2.1/unity-catalog/tables" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"IngressRuleInternetGateway\",\"catalog_name\":\"${CATALOG}\",\"schema_name\":\"${SCHEMA}\",\"table_type\":\"EXTERNAL\",\"data_source_format\":\"DELTA\",\"storage_location\":\"${DELTA_BASE}/IngressRuleInternetGateway\"}" || true
echo

echo "== Verify =="
curl -fsS "${UC_SERVER}/api/2.1/unity-catalog/catalogs" | head -c 500; echo
curl -fsS "${UC_SERVER}/api/2.1/unity-catalog/schemas?catalog_name=${CATALOG}" | head -c 500; echo
curl -fsS "${UC_SERVER}/api/2.1/unity-catalog/tables?catalog_name=${CATALOG}&schema_name=${SCHEMA}" | head -c 500; echo

echo "✅ Done: registered ${CATALOG}.${SCHEMA}.*"
