# PuppyGraph Cypher API Reference

This document contains sample Cypher requests and responses used in the cybersecurity dashboard for future reference.

## API Endpoint
- **URL**: `http://localhost:8081/submitCypher`
- **Method**: POST
- **Authentication**: Basic Auth (username: `puppygraph`, password: `puppygraph123`)
- **Content-Type**: `application/json`

## Request Format
```json
{
  "query": "<CYPHER_QUERY_STRING>"
}
```

## Response Format
The API returns an array of result objects:
```json
[
  {
    "Values": [<array_of_values>],
    "Keys": ["<column_names>"]
  }
]
```

## Sample Queries and Responses

### 1. Total Node Count
**Request:**
```bash
curl -X POST http://localhost:8081/submitCypher \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (n) RETURN count(n) as total_nodes LIMIT 1"}' \
  --user puppygraph:puppygraph123
```

**Response:**
```json
[{"Values":[65480],"Keys":["total_nodes"]}]
```

### 2. CVE Count
**Request:**
```bash
curl -X POST http://localhost:8081/submitCypher \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (cve:CVE) RETURN count(cve) as cve_count LIMIT 1"}' \
  --user puppygraph:puppygraph123
```

**Response:**
```json
[{"Values":[23070],"Keys":["cve_count"]}]
```

### 3. AWS Inspector Findings Count
**Request:**
```bash
curl -X POST http://localhost:8081/submitCypher \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (f:AWSInspectorFinding) RETURN count(f) as findings_count LIMIT 1"}' \
  --user puppygraph:puppygraph123
```

**Response:**
```json
[{"Values":[27254],"Keys":["findings_count"]}]
```

### 4. EC2 Instances Count
**Request:**
```bash
curl -X POST http://localhost:8081/submitCypher \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (ec2:EC2Instance) RETURN count(ec2) as ec2_count LIMIT 1"}' \
  --user puppygraph:puppygraph123
```

**Response:**
```json
[{"Values":[5000],"Keys":["ec2_count"]}]
```

### 5. Network Flows Count
**Request:**
```bash
curl -X POST http://localhost:8081/submitCypher \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH ()-[r:TRAFFIC_TO_EXTERNAL]->() RETURN count(r) as network_flows LIMIT 1"}' \
  --user puppygraph:puppygraph123
```

**Response:**
```json
[{"Values":[5000],"Keys":["network_flows"]}]
```

### 6. Critical CVEs with Base Score
**Request:**
```bash
curl -X POST http://localhost:8081/submitCypher \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (cve:CVE) WHERE cve.base_score >= 7.0 RETURN count(cve) as critical_cves LIMIT 1"}' \
  --user puppygraph:puppygraph123
```

**Response:**
```json
[{"Values":[11846],"Keys":["critical_cves"]}]
```

### 7. CVE Node Properties Sample
**Request:**
```bash
curl -X POST http://localhost:8081/submitCypher \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (cve:CVE) RETURN cve LIMIT 1"}' \
  --user puppygraph:puppygraph123
```

**Response:**
```json
[{"Values":[{"Id":3818394685,"ElementId":"CVE[CVE-2021-0007]","Labels":["CVE"],"Props":{}}],"Keys":["cve"]}]
```

## Dashboard Implementation Queries

### CVE Analysis Page
**Query:**
```cypher
MATCH (cve:CVE)-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)-[:HAS_FINDING]-(ec2:EC2Instance)
RETURN cve.cve_id as cve_id, cve.base_score as score, cve.description as description, 
       count(DISTINCT ec2) as affected_instances
ORDER BY cve.base_score DESC
LIMIT 50
```

### Recent Security Alerts
**Query:**
```cypher
MATCH (ec2:EC2Instance)-[:HAS_FINDING]->(finding:AWSInspectorFinding)-[:HAS_VULNERABILITY]->(cve:CVE)
WHERE cve.base_score >= 7.0
RETURN ec2.instance_id as instance, cve.cve_id as cve, cve.base_score as score, finding.title as finding_title
ORDER BY cve.base_score DESC
LIMIT 10
```

### Suspicious Network Traffic
**Query:**
```cypher
MATCH (ni:NetworkInterface)-[r:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
WHERE ext.is_malicious = true
RETURN ni.interface_id as interface_id, ext.ip_address as external_ip, r.port as port
LIMIT 10
```

### Network Analysis - Top External Connections
**Query:**
```cypher
MATCH (ni:NetworkInterface)-[r:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
RETURN ext.ip_address as ip, ext.is_malicious as is_malicious, count(r) as connection_count
ORDER BY connection_count DESC
LIMIT 10
```

### Network Analysis - Suspicious Instances
**Query:**
```cypher
MATCH (ec2:EC2Instance)-[:HAS_NETWORK_INTERFACE]->(ni:NetworkInterface)-[:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
WHERE ext.is_malicious = true
RETURN ec2.instance_id as instance, count(DISTINCT ext) as malicious_connections
ORDER BY malicious_connections DESC
LIMIT 10
```

### Network Analysis - Top Ports
**Query:**
```cypher
MATCH ()-[r:TRAFFIC_TO_EXTERNAL]->()
RETURN r.port as port, count(r) as usage_count
ORDER BY usage_count DESC
LIMIT 10
```

## Graph Schema Reference

Based on the CLAUDE.md documentation, the graph contains the following entities and relationships:

### Vertices
- **CVE**: Common Vulnerabilities and Exposures
- **AWSInspectorFinding**: AWS security findings
- **EC2Instance**: AWS EC2 compute instances
- **NetworkInterface**: Network interfaces attached to instances
- **EC2Subnet**: Network subnets containing interfaces
- **ExternalIPAddress**: External/public IP addresses with threat intelligence

### Relationships
- `CVE ← HAS_VULNERABILITY ← AWSInspectorFinding`
- `EC2Instance → HAS_FINDING → AWSInspectorFinding`
- `EC2Instance → HAS_NETWORK_INTERFACE → NetworkInterface`
- `NetworkInterface → PART_OF_SUBNET → EC2Subnet`
- `NetworkInterface → TRAFFIC_TO_EXTERNAL → ExternalIPAddress`
- `NetworkInterface → TRAFFIC_BETWEEN_INTERFACES → NetworkInterface`

## Notes
- All responses are arrays, even for single results
- Values array contains the actual data in the order specified by Keys array
- Node objects contain Id, ElementId, Labels, and Props fields
- Base authentication is required for all requests
- The API endpoint is accessible at port 8081 when the demo environment is running