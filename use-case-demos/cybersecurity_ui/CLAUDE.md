# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Start the demo environment
```bash
docker compose up -d
```

### Stop and cleanup
```bash
docker compose down --volumes --remove-orphans
```

### Generate sample data (if needed)
```bash
cd gen_data
# Download and process CVE data
wget https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-2025.json.zip
unzip nvdcve-2.0-2025.json.zip -d cve_json
python3 cve_json_to_csv.py
python3 gen_data.py
cp cve.csv ../postgres-init/csv_data/
```

## Architecture Overview

This is a cybersecurity graph demonstration using PuppyGraph to visualize AWS security data relationships. The system models cybersecurity entities as a graph with the following architecture:

### Core Components
- **PostgreSQL Database**: Stores relational data for CVEs, AWS Inspector findings, EC2 instances, network interfaces, and subnets
- **PuppyGraph**: Graph database layer that maps PostgreSQL tables to graph vertices and edges
- **Graph Schema**: Defined in `schema.json` - maps relational data to graph model

### Data Model
The graph represents cybersecurity relationships:
- **CVE vertices**: Common Vulnerabilities and Exposures
- **AWSInspectorFinding vertices**: AWS security findings
- **EC2Instance vertices**: AWS EC2 compute instances  
- **NetworkInterface vertices**: Network interfaces attached to instances
- **EC2Subnet vertices**: Network subnets containing interfaces
- **ExternalIPAddress vertices**: External/public IP addresses with threat intelligence

### Key Relationships
- CVE ← HAS_VULNERABILITY ← AWSInspectorFinding
- EC2Instance → HAS_FINDING → AWSInspectorFinding
- EC2Instance → HAS_NETWORK_INTERFACE → NetworkInterface
- NetworkInterface → PART_OF_SUBNET → EC2Subnet
- NetworkInterface → TRAFFIC_TO_EXTERNAL → ExternalIPAddress (VPC flow logs)
- NetworkInterface → TRAFFIC_BETWEEN_INTERFACES → NetworkInterface (VPC flow logs)

### Services
- **PuppyGraph UI**: http://localhost:8081 (puppygraph/puppygraph123)
- **PostgreSQL**: localhost:5432 (postgres/postgres123)
- **Graph Query Ports**: 8182 (Gremlin), 7687 (Cypher/Neo4j)

### File Structure
- `docker-compose.yaml`: Service orchestration
- `schema.json`: Graph model definition mapping PostgreSQL to graph vertices/edges
- `postgres-init/init.sql`: Database schema and data loading
- `postgres-init/csv_data/`: Sample cybersecurity data files
- `gen_data/`: Python scripts for generating sample data from CVE feeds

### VPC Flow Logs Integration
The demo models VPC flow logs as graph edges to show network traffic patterns:
- **External-facing instances** (15% of total): Web servers that communicate with external IPs
- **Internal instances** (85% of total): Backend services with limited external access
- **Threat intelligence**: External IPs include malicious indicators (10% flagged as threats)
- **Traffic analysis**: Flow logs capture accepted/rejected connections with port/protocol details

The demo supports Cypher queries to analyze security relationships like finding instances affected by CVEs, vulnerable instances in subnets, network neighbors with security risks, and traffic patterns to potentially malicious external IPs.