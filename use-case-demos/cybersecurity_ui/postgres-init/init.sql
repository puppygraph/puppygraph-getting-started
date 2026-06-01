\c cybersecurity_db;

CREATE TABLE cve (
  id                      VARCHAR(20)    PRIMARY KEY,  -- CVE identifier, e.g. CVE-2023-41782
  source_identifier       VARCHAR(128),                -- sourceIdentifier field
  published               TIMESTAMP,                   -- published timestamp
  last_modified           TIMESTAMP,                   -- lastModified timestamp
  vuln_status             VARCHAR(32),                 -- vulnStatus field
  description_en          TEXT,                        -- English description
  vector_string           VARCHAR(128),                -- CVSS v3 vector string
  base_score              NUMERIC(3,1),                -- CVSS baseScore
  base_severity           VARCHAR(16),                 -- CVSS baseSeverity
  exploitability_score    NUMERIC(3,1),
  impact_score            NUMERIC(3,1),
  weaknesses              TEXT,                        -- comma-separated CWE IDs
  reference_urls          TEXT                         -- comma-separated URLs
);

CREATE TABLE aws_inspector_findings (
  id                         VARCHAR(256)    PRIMARY KEY,     -- Reuses ARN of the finding
  region                     VARCHAR(32)     NOT NULL,        -- AWS region where the finding was generated
  title                      TEXT,                            -- Finding name/title
  instance_id                VARCHAR(64),                     -- EC2 instance ID (if applicable)
  status                     VARCHAR(16),                     -- Current status of the finding (e.g., ACTIVE, RESOLVED)
  severity                   VARCHAR(16),                     -- Severity level (e.g. LOW, MEDIUM, HIGH, CRITICAL)
  first_observed_at          TIMESTAMP,                       -- When the finding was first detected
  last_observed_at           TIMESTAMP,                       -- When the finding was last updated
  description                TEXT,                            -- Full description of the finding
  finding_type               VARCHAR(64),                     -- Type (e.g. NETWORK_REACHABILITY, PACKAGE_VULNERABILITY)
  inspector_score            NUMERIC(5,2),                    -- AWS Inspector’s own composite score
  cvss_score                 NUMERIC(3,1),                    -- CVSS base score (only for PACKAGE_VULNERABILITY)
  vulnerability_id           VARCHAR(20)                      -- Associated CVE ID (only for PACKAGE_VULNERABILITY)
);


-- Table: ec2_instances
CREATE TABLE ec2_instances (
  id                   VARCHAR(64)   PRIMARY KEY,  -- Unique EC2 instance ID (e.g., i-0123456789abcdef0)
  imageid              VARCHAR(64),                -- AMI ID used to launch the instance
  instancetype         VARCHAR(32),                -- Instance type (e.g., t2.micro, c4.large)
  iaminstanceprofile   VARCHAR(256),               -- ARN of the IAM instance profile, if assigned
  launchtime           TIMESTAMP,                  -- Timestamp when the instance was launched
  launchtimeunix       BIGINT,                     -- Launch time as Unix epoch seconds
  monitoringstate      VARCHAR(16),                -- Monitoring state (enabled, disabled, pending, disabling)
  state                VARCHAR(16),                -- Current instance state (running, stopped, terminated)
  availabilityzone     VARCHAR(32),                -- Availability Zone (e.g., us-east-1d)
  tenancy              VARCHAR(16),                -- Tenancy type (default, dedicated, host)
  architecture         VARCHAR(16),                -- CPU architecture (x86_64, arm64)
  ebsoptimized         BOOLEAN,                    -- True if instance is EBS-optimized
  bootmode             VARCHAR(32),                -- Boot mode (legacy-bios, uefi)
  instancelifecycle    VARCHAR(16),                -- Lifecycle (spot, scheduled, or empty for on-demand)
  hibernationoptions   BOOLEAN                     -- True if hibernation is enabled
);

-- Table: network_interfaces
CREATE TABLE network_interfaces (
  id                 VARCHAR(64)   PRIMARY KEY,  -- Unique network interface ID (e.g., eni-0abcdef1234567890)
  mac_address        VARCHAR(17),                 -- MAC address (e.g., 00:00:00:00:00:01)
  description        TEXT,                        -- Description of the network interface
  private_ip_address VARCHAR(64),                 -- Primary private IPv4 address (e.g., 10.0.1.3)
  private_dns_name   TEXT,                        -- Private DNS name (e.g., ip-10-0-1-3.ec2.internal)
  public_ip          VARCHAR(64),                 -- Public IPv4 address attached to the interface, if any
  status             VARCHAR(16),                 -- Interface status (available, associated, attaching, in-use, detaching)
  subnetid           VARCHAR(64),                 -- Subnet ID (e.g., subnet-0123456789abcdef0)
  interface_type     VARCHAR(16),                 -- Type of interface (interface, efa)
  source_dest_check  BOOLEAN                      -- True if source/destination checking is enabled
);

-- Table: ec2_instance_interfaces
CREATE TABLE ec2_instance_interfaces (
  instance_id    VARCHAR(64) NOT NULL
    REFERENCES ec2_instances(id) ON DELETE CASCADE,  -- EC2 instance ID (foreign key to ec2_instances)
  interface_id   VARCHAR(64) NOT NULL
    REFERENCES network_interfaces(id) ON DELETE CASCADE,  -- Network interface ID (foreign key to network_interfaces)
  PRIMARY KEY (instance_id, interface_id)  -- Composite key ensures each pair is unique
);

-- Table: ec2_subnets
CREATE TABLE ec2_subnets (
  id                          VARCHAR(64)   PRIMARY KEY,  -- The ID of the subnet (same as id)
  region                      VARCHAR(32)   NOT NULL,     -- AWS region where the subnet is located (e.g., us-east-1)
  ownerid                     VARCHAR(20),                -- AWS Account ID owning this subnet
  cidr_block                  VARCHAR(32)   NOT NULL,     -- IPv4 CIDR block assigned to the subnet (e.g., 10.0.1.0/24)
  available_ip_address_count  INTEGER,                    -- Number of unused private IPv4 addresses remaining
  default_for_az              BOOLEAN,                    -- True if this is the default subnet for its Availability Zone
  map_customer_owned_ip_on_launch BOOLEAN,                -- True if ENIs created here receive a customer-owned IPv4 address
  map_public_ip_on_launch     BOOLEAN,                    -- True if instances launched here receive a public IPv4 address
  availability_zone           VARCHAR(32),                -- Availability Zone (e.g., us-east-1d)
  availability_zone_id        VARCHAR(32),                -- AZ ID (e.g., use1-az1)
  state                       VARCHAR(16),                -- Current state of the subnet (e.g., pending, available)
  assignipv6addressoncreation BOOLEAN                     -- True if ENIs created here receive an IPv6 address
);

-- Table: vpc_flow_to_external
CREATE TABLE vpc_flow_to_external (
  id                      VARCHAR(128)   PRIMARY KEY,     -- Unique flow log record ID
  from_interface_id       VARCHAR(64)    NOT NULL,        -- Source network interface ID (eni-xxx)
  to_external_ip          VARCHAR(64)    NOT NULL,        -- Destination external IP address
  srcport                 INTEGER,                        -- Source port number
  dstport                 INTEGER,                        -- Destination port number
  protocol                INTEGER,                        -- IP protocol number (e.g., 6=TCP, 17=UDP)
  packets                 BIGINT,                         -- Number of packets
  bytes                   BIGINT,                         -- Number of bytes
  windowstart             BIGINT,                         -- Start time window (Unix timestamp)
  windowend               BIGINT,                         -- End time window (Unix timestamp)
  action                  VARCHAR(16),                    -- ACCEPT or REJECT
  flowlogstatus           VARCHAR(16),                    -- OK, NODATA, SKIPDATA
  flow_direction          VARCHAR(16),                    -- ingress or egress
  region                  VARCHAR(32),                    -- AWS region
  account_id              VARCHAR(20),                    -- AWS Account ID
  tcp_flags               INTEGER,                        -- TCP flags bitmask
  traffic_path            INTEGER                         -- Traffic path through AWS network
);

-- Table: vpc_flow_between_interfaces  
CREATE TABLE vpc_flow_between_interfaces (
  id                      VARCHAR(128)   PRIMARY KEY,     -- Unique flow log record ID
  from_interface_id       VARCHAR(64)    NOT NULL,        -- Source network interface ID (eni-xxx)
  to_interface_id         VARCHAR(64)    NOT NULL,        -- Destination network interface ID (eni-xxx)
  srcport                 INTEGER,                        -- Source port number
  dstport                 INTEGER,                        -- Destination port number
  protocol                INTEGER,                        -- IP protocol number (e.g., 6=TCP, 17=UDP)
  packets                 BIGINT,                         -- Number of packets
  bytes                   BIGINT,                         -- Number of bytes
  windowstart             BIGINT,                         -- Start time window (Unix timestamp)
  windowend               BIGINT,                         -- End time window (Unix timestamp)
  action                  VARCHAR(16),                    -- ACCEPT or REJECT
  flowlogstatus           VARCHAR(16),                    -- OK, NODATA, SKIPDATA
  flow_direction          VARCHAR(16),                    -- ingress or egress
  region                  VARCHAR(32),                    -- AWS region
  account_id              VARCHAR(20),                    -- AWS Account ID
  tcp_flags               INTEGER,                        -- TCP flags bitmask
  traffic_path            INTEGER                         -- Traffic path through AWS network
);

-- Table: external_ip_addresses
CREATE TABLE external_ip_addresses (
  ip_address              VARCHAR(64)    PRIMARY KEY,     -- External IP address
  ip_type                 VARCHAR(16),                    -- Type: public, private, unknown
  geolocation_country     VARCHAR(64),                    -- Country (if available)
  geolocation_region      VARCHAR(64),                    -- Region/State (if available)
  geolocation_city        VARCHAR(64),                    -- City (if available)
  asn                     INTEGER,                        -- Autonomous System Number
  as_org                  VARCHAR(256),                   -- AS Organization name
  is_known_malicious      BOOLEAN,                        -- True if flagged as malicious
  threat_category         VARCHAR(64),                    -- Threat category (e.g., botnet, scanner)
  first_seen              TIMESTAMP,                      -- First time this IP was observed
  last_seen               TIMESTAMP,                      -- Last time this IP was observed
  reputation_score        INTEGER                         -- Reputation score (0-100, lower is worse)
);





COPY cve FROM '/docker-entrypoint-initdb.d/csv_data/cve.csv' CSV HEADER;
COPY aws_inspector_findings FROM '/docker-entrypoint-initdb.d/csv_data/aws_inspector_findings.csv' CSV HEADER;
COPY ec2_instances FROM '/docker-entrypoint-initdb.d/csv_data/ec2_instances.csv' CSV HEADER;
COPY network_interfaces FROM '/docker-entrypoint-initdb.d/csv_data/network_interfaces.csv' CSV HEADER;
COPY ec2_instance_interfaces FROM '/docker-entrypoint-initdb.d/csv_data/ec2_instance_interfaces.csv' CSV HEADER;
COPY ec2_subnets FROM '/docker-entrypoint-initdb.d/csv_data/ec2_subnets.csv' CSV HEADER;
COPY vpc_flow_to_external FROM '/docker-entrypoint-initdb.d/csv_data/vpc_flow_to_external.csv' CSV HEADER;
COPY vpc_flow_between_interfaces FROM '/docker-entrypoint-initdb.d/csv_data/vpc_flow_between_interfaces.csv' CSV HEADER;
COPY external_ip_addresses FROM '/docker-entrypoint-initdb.d/csv_data/external_ip_addresses.csv' CSV HEADER;
