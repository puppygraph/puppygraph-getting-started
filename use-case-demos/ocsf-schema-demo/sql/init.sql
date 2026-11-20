-- Account Change Events
CREATE TABLE IF NOT EXISTS account_change_events (
    event_id VARCHAR(50) PRIMARY KEY,
    target_user_id VARCHAR(50),
    initiated_by_user_id VARCHAR(50),
    change_type VARCHAR(50),
    change_details TEXT,
    timestamp TIMESTAMP,
    outcome VARCHAR(50),
    severity VARCHAR(20)
);
COPY account_change_events FROM '/data/account_change_events.csv' DELIMITER ',' CSV HEADER;

-- Authentication Events
CREATE TABLE IF NOT EXISTS authentication_events (
    event_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    device_id VARCHAR(50),
    auth_type VARCHAR(50),
    outcome VARCHAR(50),
    timestamp TIMESTAMP,
    source_ip VARCHAR(45),
    country_code VARCHAR(10),
    is_mfa_enabled BOOLEAN
);
COPY authentication_events FROM '/data/authentication_events.csv' DELIMITER ',' CSV HEADER;

-- Device Resource Relationships
CREATE TABLE IF NOT EXISTS device_resource_relationships (
    device_id VARCHAR(50),
    resource_id VARCHAR(50),
    access_count BIGINT,
    last_access TIMESTAMP,
    PRIMARY KEY (device_id, resource_id)
);
COPY device_resource_relationships FROM '/data/device_resource_relationships.csv' DELIMITER ',' CSV HEADER;

-- Devices (Matches nodes_device concept)
CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(50) PRIMARY KEY,
    hostname VARCHAR(255),
    os_type VARCHAR(100),
    os_version VARCHAR(100),
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    owner_user_id VARCHAR(50),
    device_type VARCHAR(50),
    is_privileged BOOLEAN,
    risk_score INT,
    created_at TIMESTAMP
);
COPY devices FROM '/data/devices.csv' DELIMITER ',' CSV HEADER;

-- File Activity Events
CREATE TABLE IF NOT EXISTS file_activity_events (
    event_id VARCHAR(50) PRIMARY KEY,
    device_id VARCHAR(50),
    filepath TEXT,
    operation VARCHAR(50),
    user_id VARCHAR(50),
    timestamp TIMESTAMP,
    severity VARCHAR(20),
    outcome VARCHAR(50)
);
COPY file_activity_events FROM '/data/file_activity_events.csv' DELIMITER ',' CSV HEADER;

-- Malware Detection Alerts
CREATE TABLE IF NOT EXISTS malware_detection_alerts (
    event_id VARCHAR(50) PRIMARY KEY,
    device_id VARCHAR(50),
    malware_family VARCHAR(100),
    malware_name VARCHAR(100),
    filepath TEXT,
    detection_time TIMESTAMP,
    action VARCHAR(50),
    severity VARCHAR(20)
);
COPY malware_detection_alerts FROM '/data/malware_detection_alerts.csv' DELIMITER ',' CSV HEADER;

-- Network Flows (Matches nodes_network_flow concept)
CREATE TABLE IF NOT EXISTS network_flows (
    flow_id VARCHAR(50) PRIMARY KEY,
    src_device_id VARCHAR(50),
    dst_device_id VARCHAR(50),
    src_ip VARCHAR(45),
    dst_ip VARCHAR(45),
    src_port INT,
    dst_port INT,
    protocol VARCHAR(20),
    bytes_sent BIGINT,
    bytes_received BIGINT,
    packet_count BIGINT,
    duration_seconds BIGINT,
    timestamp TIMESTAMP,
    status VARCHAR(50),
    severity VARCHAR(20)
);
COPY network_flows FROM '/data/network_flows.csv' DELIMITER ',' CSV HEADER;

-- Policy Violation Events
CREATE TABLE IF NOT EXISTS policy_violation_events (
    event_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    device_id VARCHAR(50),
    violation_type VARCHAR(100),
    policy_name VARCHAR(100),
    timestamp TIMESTAMP,
    severity VARCHAR(20),
    action_taken VARCHAR(50)
);
COPY policy_violation_events FROM '/data/policy_violation_events.csv' DELIMITER ',' CSV HEADER;

-- Privilege Escalation Events
CREATE TABLE IF NOT EXISTS privilege_escalation_events (
    event_id VARCHAR(50) PRIMARY KEY,
    device_id VARCHAR(50),
    user_id VARCHAR(50),
    escalation_type VARCHAR(50),
    from_privilege_level VARCHAR(50),
    to_privilege_level VARCHAR(50),
    outcome VARCHAR(50),
    timestamp TIMESTAMP,
    severity VARCHAR(20)
);
COPY privilege_escalation_events FROM '/data/privilege_escalation_events.csv' DELIMITER ',' CSV HEADER;

-- Process Execution Events
CREATE TABLE IF NOT EXISTS process_execution_events (
    event_id VARCHAR(50) PRIMARY KEY,
    device_id VARCHAR(50),
    process_name VARCHAR(255),
    process_id BIGINT,
    parent_process_id BIGINT,
    command_line TEXT,
    user_id VARCHAR(50),
    timestamp TIMESTAMP,
    severity VARCHAR(20),
    outcome VARCHAR(50)
);
COPY process_execution_events FROM '/data/process_execution_events.csv' DELIMITER ',' CSV HEADER;
-- Resource Access Events
CREATE TABLE IF NOT EXISTS resource_access_events (
    event_id VARCHAR(50) PRIMARY KEY,
    device_id VARCHAR(50),
    resource_id VARCHAR(50),
    access_type VARCHAR(50),
    outcome VARCHAR(50),
    timestamp TIMESTAMP,
    data_size_bytes BIGINT
);
COPY resource_access_events FROM '/data/resource_access_events.csv' DELIMITER ',' CSV HEADER;

-- Resources
CREATE TABLE IF NOT EXISTS resources (
    resource_id VARCHAR(50) PRIMARY KEY,
    resource_name VARCHAR(255),
    resource_type VARCHAR(50),
    criticality VARCHAR(50),
    owner_user_id VARCHAR(50),
    location VARCHAR(50),
    contains_pii BOOLEAN,
    contains_phi BOOLEAN
);
COPY resources FROM '/data/resources.csv' DELIMITER ',' CSV HEADER;

-- User Device Relationships
CREATE TABLE IF NOT EXISTS user_device_relationships (
    user_id VARCHAR(50),
    device_id VARCHAR(50),
    access_type VARCHAR(50),
    last_access TIMESTAMP,
    PRIMARY KEY (user_id, device_id)
);
COPY user_device_relationships FROM '/data/user_device_relationships.csv' DELIMITER ',' CSV HEADER;

-- Users
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(100),
    department VARCHAR(100),
    role VARCHAR(100),
    is_admin BOOLEAN,
    is_contractor BOOLEAN,
    manager_id VARCHAR(50),
    created_at TIMESTAMP
);
COPY users FROM '/data/users.csv' DELIMITER ',' CSV HEADER;