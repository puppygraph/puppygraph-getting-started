#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_DIR="$SCRIPT_DIR/csv_data"
SERVICE="${CLICKHOUSE_SERVICE:-clickhouse}"
DB="cspm"

ch() { docker compose exec -T "$SERVICE" clickhouse-client --input_format_defaults_for_omitted_fields=0 "$@"; }

echo "Creating schema..."
ch --multiquery <<SQL
CREATE DATABASE IF NOT EXISTS ${DB};

CREATE TABLE IF NOT EXISTS ${DB}.Users (
    user_id UInt64,
    username String,
    email String,
    phone String,
    created_at DateTime,
    last_login DateTime,
    account_status LowCardinality(String),
    authentication_method LowCardinality(String),
    failed_login_attempts UInt32
) ENGINE = MergeTree ORDER BY user_id;

CREATE TABLE IF NOT EXISTS ${DB}.InternetGateways (
    internet_gateway_id UInt64,
    name String,
    region LowCardinality(String),
    status LowCardinality(String)
) ENGINE = MergeTree ORDER BY internet_gateway_id;

CREATE TABLE IF NOT EXISTS ${DB}.VPCs (
    vpc_id UInt64,
    name String
) ENGINE = MergeTree ORDER BY vpc_id;

CREATE TABLE IF NOT EXISTS ${DB}.InternetGatewayVPC (
    internet_gateway_id UInt64,
    vpc_id UInt64
) ENGINE = MergeTree ORDER BY (internet_gateway_id, vpc_id);

CREATE TABLE IF NOT EXISTS ${DB}.Subnets (
    subnet_id UInt64,
    vpc_id UInt64,
    name String
) ENGINE = MergeTree ORDER BY subnet_id;

CREATE TABLE IF NOT EXISTS ${DB}.SecurityGroups (
    security_group_id UInt64,
    name String
) ENGINE = MergeTree ORDER BY security_group_id;

CREATE TABLE IF NOT EXISTS ${DB}.NetworkInterfaces (
    network_interface_id UInt64,
    subnet_id UInt64,
    security_group_id UInt64,
    name String
) ENGINE = MergeTree ORDER BY network_interface_id;

CREATE TABLE IF NOT EXISTS ${DB}.VMInstances (
    vm_instance_id UInt64,
    network_interface_id UInt64,
    role_id UInt64,
    name String
) ENGINE = MergeTree ORDER BY vm_instance_id;

CREATE TABLE IF NOT EXISTS ${DB}.Roles (
    role_id UInt64,
    name String
) ENGINE = MergeTree ORDER BY role_id;

CREATE TABLE IF NOT EXISTS ${DB}.Resources (
    resource_id UInt64,
    name String,
    type LowCardinality(String),
    sensitivity LowCardinality(String)
) ENGINE = MergeTree ORDER BY resource_id;

CREATE TABLE IF NOT EXISTS ${DB}.RoleResourceAccess (
    role_id UInt64,
    resource_id UInt64
) ENGINE = MergeTree ORDER BY (role_id, resource_id);

CREATE TABLE IF NOT EXISTS ${DB}.UserRoleAssumption (
    user_id UInt64,
    role_id UInt64,
    granted_at DateTime
) ENGINE = MergeTree ORDER BY (user_id, role_id);

CREATE TABLE IF NOT EXISTS ${DB}.RoleAssumeRole (
    from_role_id UInt64,
    to_role_id UInt64
) ENGINE = MergeTree ORDER BY (from_role_id, to_role_id);

CREATE TABLE IF NOT EXISTS ${DB}.PublicIPs (
    public_ip_id UInt64,
    ip_address String,
    network_interface_id UInt64
) ENGINE = MergeTree ORDER BY public_ip_id;

CREATE TABLE IF NOT EXISTS ${DB}.IngressRules (
    ingress_rule_id UInt64,
    security_group_id UInt64,
    protocol LowCardinality(String),
    port_range String,
    source String
) ENGINE = MergeTree ORDER BY ingress_rule_id;

SQL

echo "Loading CSVs..."
for csv in "$CSV_DIR"/*.csv; do
  table=$(basename "$csv" .csv)
  echo "  $table..."
  ch --database="$DB" --query="TRUNCATE TABLE IF EXISTS $table"
  ch --database="$DB" --query="INSERT INTO $table FORMAT CSVWithNames" < "$csv"
done

echo
echo "Row counts:"
ch --database="$DB" --query="SELECT name, total_rows FROM system.tables WHERE database='$DB' ORDER BY name FORMAT PrettyCompact"
