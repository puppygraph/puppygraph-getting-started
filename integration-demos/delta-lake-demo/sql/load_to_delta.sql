-- USERS
CREATE TABLE IF NOT EXISTS delta.`file:///delta/demo/Users` (
  user_id BIGINT,
  username STRING,
  email STRING,
  phone STRING,
  created_at TIMESTAMP,
  last_login TIMESTAMP,
  account_status STRING,
  authentication_method STRING,
  failed_login_attempts INT
) USING DELTA;

INSERT INTO puppygraph.demo.Users
SELECT
  user_id, username, email, phone,
  CAST(created_at AS TIMESTAMP),
  CAST(last_login AS TIMESTAMP),
  account_status, authentication_method, failed_login_attempts
FROM parquet.`/parquet_data/Users.parquet`;

-- INTERNET GATEWAYS
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/InternetGateways` (
  internet_gateway_id BIGINT,
  name STRING,
  region STRING,
  status STRING
) USING DELTA;

INSERT INTO puppygraph.demo.InternetGateways
SELECT * FROM parquet.`/parquet_data/InternetGateways.parquet`;

CREATE TABLE IF NOT EXISTS delta.`/delta/demo/UserInternetGatewayAccess` (
  user_id BIGINT,
  internet_gateway_id BIGINT,
  access_level STRING,
  granted_at TIMESTAMP,
  expires_at TIMESTAMP,
  last_accessed_at TIMESTAMP
) USING DELTA;

-- ACCESS
INSERT INTO puppygraph.demo.UserInternetGatewayAccess
SELECT
  user_id,
  internet_gateway_id,
  access_level,
  CAST(granted_at AS TIMESTAMP),
  CAST(expires_at AS TIMESTAMP),
  CAST(last_accessed_at AS TIMESTAMP)
FROM parquet.`/parquet_data/UserInternetGatewayAccess.parquet`;

-- ACCESS_RECORD
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/UserInternetGatewayAccessLog` (
  log_id BIGINT,
  user_id BIGINT,
  internet_gateway_id BIGINT,
  access_time TIMESTAMP
) USING DELTA;

INSERT INTO puppygraph.demo.UserInternetGatewayAccessLog
SELECT
  log_id,
  user_id,
  internet_gateway_id,
  CAST(access_time AS TIMESTAMP)
FROM parquet.`/parquet_data/UserInternetGatewayAccessLog.parquet`;

-- VPCS
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/VPCs` (
  vpc_id BIGINT,
  name STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS delta.`/delta/demo/InternetGatewayVPC` (
  internet_gateway_id BIGINT,
  vpc_id BIGINT
) USING DELTA;

INSERT INTO puppygraph.demo.VPCs
SELECT * FROM parquet.`/parquet_data/VPCs.parquet`;

-- IGW ↔ VPC
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/InternetGatewayVPC` (
  internet_gateway_id BIGINT,
  vpc_id BIGINT
) USING DELTA;

INSERT INTO puppygraph.demo.InternetGatewayVPC
SELECT * FROM parquet.`/parquet_data/InternetGatewayVPC.parquet`;

-- SUBNETS
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/Subnets` (
  subnet_id BIGINT,
  vpc_id BIGINT,
  name STRING
) USING DELTA;

INSERT INTO puppygraph.demo.Subnets
SELECT * FROM parquet.`/parquet_data/Subnets.parquet`;

-- SECURITY GROUPS
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/SecurityGroups` (
  security_group_id BIGINT,
  name STRING
) USING DELTA;

INSERT INTO puppygraph.demo.SecurityGroups
SELECT * FROM parquet.`/parquet_data/SecurityGroups.parquet`;

-- SUBNET ↔ SG
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/SubnetSecurityGroup` (
  subnet_id BIGINT,
  security_group_id BIGINT
) USING DELTA;

INSERT INTO puppygraph.demo.SubnetSecurityGroup
SELECT * FROM parquet.`/parquet_data/SubnetSecurityGroup.parquet`;

-- NETWORK INTERFACES
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/NetworkInterfaces` (
  network_interface_id BIGINT,
  subnet_id BIGINT,
  security_group_id BIGINT,
  name STRING
) USING DELTA;

INSERT INTO puppygraph.demo.NetworkInterfaces
SELECT * FROM parquet.`/parquet_data/NetworkInterfaces.parquet`;

-- VM INSTANCES
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/VMInstances` (
  vm_instance_id BIGINT,
  network_interface_id BIGINT,
  role_id BIGINT,
  name STRING
) USING DELTA;

INSERT INTO puppygraph.demo.VMInstances
SELECT * FROM parquet.`/parquet_data/VMInstances.parquet`;

-- ROLES
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/Roles` (
  role_id BIGINT,
  name STRING
) USING DELTA;

INSERT INTO puppygraph.demo.Roles
SELECT * FROM parquet.`/parquet_data/Roles.parquet`;

-- RESOURCES
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/Resources` (
  resource_id BIGINT,
  name STRING
) USING DELTA;

INSERT INTO puppygraph.demo.Resources
SELECT * FROM parquet.`/parquet_data/Resources.parquet`;

-- ROLE ↔ RESOURCE
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/RoleResourceAccess` (
  role_id BIGINT,
  resource_id BIGINT
) USING DELTA;

INSERT INTO puppygraph.demo.RoleResourceAccess
SELECT * FROM parquet.`/parquet_data/RoleResourceAccess.parquet`;

-- PUBLIC IPS
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/PublicIPs` (
  public_ip_id BIGINT,
  ip_address STRING,
  network_interface_id BIGINT
) USING DELTA;

INSERT INTO puppygraph.demo.PublicIPs
SELECT * FROM parquet.`/parquet_data/PublicIPs.parquet`;

-- PRIVATE IPS
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/PrivateIPs` (
  private_ip_id BIGINT,
  ip_address STRING,
  network_interface_id BIGINT
) USING DELTA;

INSERT INTO puppygraph.demo.PrivateIPs
SELECT * FROM parquet.`/parquet_data/PrivateIPs.parquet`;

-- INGRESS RULES
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/IngressRules` (
  ingress_rule_id BIGINT,
  security_group_id BIGINT,
  protocol STRING,
  port_range STRING,
  source STRING
) USING DELTA;

INSERT INTO puppygraph.demo.IngressRules
SELECT * FROM parquet.`/parquet_data/IngressRules.parquet`;

-- INGRESS RULE ↔ IGW
CREATE TABLE IF NOT EXISTS delta.`/delta/demo/IngressRuleInternetGateway` (
  ingress_rule_id BIGINT,
  internet_gateway_id BIGINT
) USING DELTA;

INSERT INTO puppygraph.demo.IngressRuleInternetGateway
SELECT * FROM parquet.`/parquet_data/IngressRuleInternetGateway.parquet`;