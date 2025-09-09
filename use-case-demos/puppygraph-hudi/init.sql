DROP DATABASE IF EXISTS security_graph CASCADE;
CREATE DATABASE IF NOT EXISTS security_graph LOCATION 's3a://warehouse/security_graph.db';
USE security_graph;

CREATE TABLE security_graph.Users
USING hudi
LOCATION 's3a://warehouse/security_graph.db/users'
TBLPROPERTIES (
  primaryKey='user_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(user_id AS BIGINT)               AS user_id,
  CAST(username AS STRING)              AS username,
  CAST(email AS STRING)                 AS email,
  CAST(phone AS STRING)                 AS phone,
  CAST(created_at AS TIMESTAMP)         AS created_at,
  CAST(last_login  AS TIMESTAMP)        AS last_login,
  CAST(account_status AS STRING)        AS account_status,
  CAST(authentication_method AS STRING) AS authentication_method,
  CAST(failed_login_attempts AS BIGINT) AS failed_login_attempts
FROM parquet.`/parquet_data/Users.parquet`;

CREATE TABLE security_graph.InternetGateways
USING hudi
LOCATION 's3a://warehouse/security_graph.db/internet_gateways'
TBLPROPERTIES (
  primaryKey='internet_gateway_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(internet_gateway_id AS BIGINT) AS internet_gateway_id,
  CAST(name AS STRING)                AS name,
  CAST(region AS STRING)              AS region,
  CAST(status AS STRING)              AS status
FROM parquet.`/parquet_data/InternetGateways.parquet`;

CREATE TABLE security_graph.UserInternetGatewayAccess
USING hudi
LOCATION 's3a://warehouse/security_graph.db/user_internet_gateway_access'
TBLPROPERTIES (
  primaryKey='user_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(user_id AS BIGINT)             AS user_id,
  CAST(internet_gateway_id AS BIGINT) AS internet_gateway_id,
  CAST(access_level AS STRING)        AS access_level,
  CAST(granted_at AS TIMESTAMP)       AS granted_at,
  CAST(expires_at AS TIMESTAMP)       AS expires_at,
  CAST(last_accessed_at AS TIMESTAMP) AS last_accessed_at
FROM parquet.`/parquet_data/UserInternetGatewayAccess.parquet`;

CREATE TABLE security_graph.UserInternetGatewayAccessLog
USING hudi
LOCATION 's3a://warehouse/security_graph.db/user_internet_gateway_access_log'
TBLPROPERTIES (
  primaryKey='log_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(log_id AS BIGINT)              AS log_id,
  CAST(user_id AS BIGINT)             AS user_id,
  CAST(internet_gateway_id AS BIGINT) AS internet_gateway_id,
  CAST(access_time AS TIMESTAMP)      AS access_time
FROM parquet.`/parquet_data/UserInternetGatewayAccessLog.parquet`;

CREATE TABLE security_graph.VPCs
USING hudi
LOCATION 's3a://warehouse/security_graph.db/vpcs'
TBLPROPERTIES (
  primaryKey='vpc_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(vpc_id AS BIGINT) AS vpc_id,
  CAST(name AS STRING)   AS name
FROM parquet.`/parquet_data/VPCs.parquet`;

CREATE TABLE security_graph.InternetGatewayVPC
USING hudi
LOCATION 's3a://warehouse/security_graph.db/internet_gateway_vpc'
TBLPROPERTIES (
  primaryKey='internet_gateway_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(internet_gateway_id AS BIGINT) AS internet_gateway_id,
  CAST(vpc_id AS BIGINT)              AS vpc_id
FROM parquet.`/parquet_data/InternetGatewayVPC.parquet`;

CREATE TABLE security_graph.Subnets
USING hudi
LOCATION 's3a://warehouse/security_graph.db/subnets'
TBLPROPERTIES (
  primaryKey='subnet_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(subnet_id AS BIGINT) AS subnet_id,
  CAST(vpc_id AS BIGINT)    AS vpc_id,
  CAST(name AS STRING)      AS name
FROM parquet.`/parquet_data/Subnets.parquet`;

CREATE TABLE security_graph.SecurityGroups
USING hudi
LOCATION 's3a://warehouse/security_graph.db/security_groups'
TBLPROPERTIES (
  primaryKey='security_group_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(security_group_id AS BIGINT) AS security_group_id,
  CAST(name AS STRING)              AS name
FROM parquet.`/parquet_data/SecurityGroups.parquet`;

CREATE TABLE security_graph.SubnetSecurityGroup
USING hudi
LOCATION 's3a://warehouse/security_graph.db/subnet_security_group'
TBLPROPERTIES (
  primaryKey='subnet_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(subnet_id AS BIGINT)         AS subnet_id,
  CAST(security_group_id AS BIGINT) AS security_group_id
FROM parquet.`/parquet_data/SubnetSecurityGroup.parquet`;

CREATE TABLE security_graph.NetworkInterfaces
USING hudi
LOCATION 's3a://warehouse/security_graph.db/network_interfaces'
TBLPROPERTIES (
  primaryKey='network_interface_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(network_interface_id AS BIGINT) AS network_interface_id,
  CAST(subnet_id AS BIGINT)            AS subnet_id,
  CAST(security_group_id AS BIGINT)    AS security_group_id,
  CAST(name AS STRING)                 AS name
FROM parquet.`/parquet_data/NetworkInterfaces.parquet`;

CREATE TABLE security_graph.VMInstances
USING hudi
LOCATION 's3a://warehouse/security_graph.db/vm_instances'
TBLPROPERTIES (
  primaryKey='vm_instance_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(vm_instance_id AS BIGINT)       AS vm_instance_id,
  CAST(network_interface_id AS BIGINT) AS network_interface_id,
  CAST(role_id AS BIGINT)              AS role_id,
  CAST(name AS STRING)                 AS name
FROM parquet.`/parquet_data/VMInstances.parquet`;

CREATE TABLE security_graph.Roles
USING hudi
LOCATION 's3a://warehouse/security_graph.db/roles'
TBLPROPERTIES (
  primaryKey='role_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(role_id AS BIGINT) AS role_id,
  CAST(name AS STRING)    AS name
FROM parquet.`/parquet_data/Roles.parquet`;

CREATE TABLE security_graph.Resources
USING hudi
LOCATION 's3a://warehouse/security_graph.db/resources'
TBLPROPERTIES (
  primaryKey='resource_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(resource_id AS BIGINT) AS resource_id,
  CAST(name AS STRING)        AS name
FROM parquet.`/parquet_data/Resources.parquet`;

CREATE TABLE security_graph.RoleResourceAccess
USING hudi
LOCATION 's3a://warehouse/security_graph.db/role_resource_access'
TBLPROPERTIES (
  primaryKey='role_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(role_id AS BIGINT)     AS role_id,
  CAST(resource_id AS BIGINT) AS resource_id
FROM parquet.`/parquet_data/RoleResourceAccess.parquet`;

CREATE TABLE security_graph.PublicIPs
USING hudi
LOCATION 's3a://warehouse/security_graph.db/public_ips'
TBLPROPERTIES (
  primaryKey='public_ip_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(public_ip_id AS BIGINT)        AS public_ip_id,
  CAST(network_interface_id AS BIGINT) AS network_interface_id,
  CAST(ip_address AS STRING)          AS ip_address
FROM parquet.`/parquet_data/PublicIPs.parquet`;

CREATE TABLE security_graph.PrivateIPs
USING hudi
LOCATION 's3a://warehouse/security_graph.db/private_ips'
TBLPROPERTIES (
  primaryKey='private_ip_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(private_ip_id AS BIGINT)        AS private_ip_id,
  CAST(network_interface_id AS BIGINT) AS network_interface_id,
  CAST(ip_address AS STRING)           AS ip_address
FROM parquet.`/parquet_data/PrivateIPs.parquet`;

CREATE TABLE security_graph.IngressRules
USING hudi
LOCATION 's3a://warehouse/security_graph.db/ingress_rules'
TBLPROPERTIES (
  primaryKey='ingress_rule_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(ingress_rule_id AS BIGINT)   AS ingress_rule_id,
  CAST(security_group_id AS BIGINT) AS security_group_id,
  CAST(protocol AS STRING)          AS protocol,
  CAST(port_range AS STRING)        AS port_range,
  CAST(source AS STRING)            AS source
FROM parquet.`/parquet_data/IngressRules.parquet`;

CREATE TABLE security_graph.IngressRuleInternetGateway
USING hudi
LOCATION 's3a://warehouse/security_graph.db/ingress_rule_internet_gateway'
TBLPROPERTIES (
  primaryKey='ingress_rule_id',
  'hoodie.metadata.enable'='true'
)
AS
SELECT
  CAST(ingress_rule_id AS BIGINT)     AS ingress_rule_id,
  CAST(internet_gateway_id AS BIGINT) AS internet_gateway_id
FROM parquet.`/parquet_data/IngressRuleInternetGateway.parquet`;