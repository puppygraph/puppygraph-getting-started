# OCSF Cyber-Threat Knowledge Graph Demo (using PuppyGraph)

## Summary

This demo showcases how to investigate cyber threats and visualize attack paths across a security environment using PuppyGraph's graph querying capabilities, running directly over raw PostgreSQL tables with no ETL required.

By modeling security telemetry as a graph over [OCSF (Open Cybersecurity Schema Framework)](https://schema.ocsf.io/) event data, users can trace complex attack scenarios such as:
* Non-admin users authenticating to devices and executing malicious tools
* Devices moving laterally through the network to access critical resources
* Users successfully escalating their privileges to admin level

Using Cypher queries, users can traverse the security graph to reconstruct attack chains and uncover threats that would otherwise require expensive multi-table joins across siloed event logs. This practical approach demonstrates how graph traversal simplifies incident investigation and security auditing at scale.

**Overview:**
- **`docker-compose.yml`**: Defines the docker services needed to run the demo. This includes both the PostgreSQL database and the PuppyGraph instance.
- **`data/`**: Contains raw CSV source files for all entities.
- **`sql/init.sql`**: SQL script for table creation and importing CSV data into PostgreSQL.
- **`schema.json`**: Complete graph mapping configuration for PuppyGraph.

## Prerequisites

- Docker

## Deployment

Start PostgreSQL and PuppyGraph by running:

```bash
docker compose up -d
```

Example output:

```bash
[+] Running 3/3
✔ Network puppy-postgres        Created
✔ Container postgres            Started
✔ Container puppygraph          Started
```

## PuppyGraph Setup

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
   - Username: `puppygraph`
   - Password: `puppygraph123`

2. Upload the schema:
   - Select the file `schema.json` in the Upload Graph Schema JSON section and click on Upload.

## Querying the Graph

Navigate to the Query panel on the left side. The Graph Query tab offers an interactive environment for querying the graph using Gremlin and Cypher.

After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. You can do this by clicking the **Clear Canvas** button located in the top-right corner of the page.

### Example Queries

#### 1. Blast Radius

Find attack chains where a non-admin user login is followed by malicious tool execution and critical resource access.

```cypher
MATCH (u:User)-[auth:Authenticated]->(d:Device)
MATCH (d)-[run:RunningProcess]->(p:Process)
MATCH (d)-[acc:AccessedResource]->(r:Resource)
WHERE u.is_admin = false
  AND p.name IN ['mimikatz.exe', 'ncat.exe', 'psexec.exe', 'impacket']
  AND r.criticality IN ['critical', 'high']
  AND auth.timestamp < run.timestamp
  AND run.timestamp < acc.timestamp
RETURN u, auth, d, run, p, acc, r
```

#### 2. Lateral Movement Analysis

Trace kill chains where a compromised device moves laterally to a victim server that then accesses a critical resource.

```cypher
MATCH path = (attacker:Device)-[flow:NetworkFlow]->(victim:Device)-[access:AccessedResource]->(target:Resource)
WHERE target.criticality IN ['critical', 'high']
  // Ensure we aren't catching self-loops (internal processing)
  AND attacker <> victim
  // Time causality
  AND flow.timestamp < access.timestamp
RETURN path
LIMIT 20
```

#### 3. Privilege Escalation Detection

Identify non-admin users who successfully escalated privileges to Admin level on a device.

```cypher
MATCH (u:User)-[esc:EscalatedPrivilege]->(d:Device)
WHERE u.is_admin = false
  AND esc.outcome = 'success' // Remove this line to also see failed attempts
RETURN
  u.username AS Suspicious_User,
  esc.escalation_type AS Attack_Method,
  d.hostname AS Target_Device,
  esc.outcome AS Result
```

## Cleanup

To stop and remove the containers, run:

```bash
docker compose down
```
