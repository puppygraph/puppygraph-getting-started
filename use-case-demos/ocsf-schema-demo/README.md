## **OCSF Cyber-Threat Knowledge Graph Demo (using PuppyGraph)**
In most security stacks, identity logs, network traffic and endpoint events are stored in separate systems. This makes it difficult to reconstruct what actually happened during an incident without stitching together many different data sources.

In this project, we'll map a slice of [OCSF (Open Cybersecurity Schema Framework)](https://schema.ocsf.io/) into a graph using PuppyGraph, directly over the raw event tables (zero ETL).

The purpose of this work is to show that treating security telemetry as a connected graph makes investigation simpler and more natural than working with isolated event records and multi-table joins.

---

### **Examples of Analytical Use-Cases (Cypher Queries)**

#### 1. **Blast Radius**
Ques: Find the attack chain where a non-admin user login is followed by the execution of malicious tools (e.g., Mimikatz) that subsequently access critical resources.

Query to obtain a list of attack chain objects:
```cypher
MATCH (u:User)-[auth:Authenticated]->(d:Device)
MATCH (d)-[run:RunningProcess]->(p:Process)
MATCH (d)-[acc:AccessedResource]->(r:Resource)
WHERE u.is_admin = false
  //Filter for malicious tools
  AND p.name IN ['mimikatz. exe', 'ncat. exe', 'psexec.exe', 'impacket']
  AND r.criticality IN ['critical', 'high']
  //Strict Time Causality: Login -> Process Run -> Data Access
  AND auth.timestamp < run.timestamp
  AND run.timestamp < acc.timestamp
RETURN u.username AS Actor, p.name AS Malicious_Tool, d.hostname AS Compromised_Device, r.resource_name AS Target_Asset
```

Query to visualize the actual forked paths (from devices to malicious processes and exposed resources):
```cypher
MATCH (u:User)-[auth:Authenticated]->(d:Device)
MATCH (d)-[run:RunningProcess]->(p:Process)
MATCH (d)-[acc:AccessedResource]->(r:Resource)
WHERE u.is_admin = false
  AND p.name IN ['mimikatz. exe', 'ncat. exe', 'psexec.exe', 'impacket']
  AND r.criticality IN ['critical', 'high']
  AND auth.timestamp < run.timestamp
  AND run.timestamp < acc.timestamp
RETURN u, auth, d, run, p, acc, r
```
* SQL Pain Point: (performance nightmare)
    *  requires joining Endpoint Logs, User and Device Tables and Data Access Logs 
    * then filtering by a calculated time-delta between two massive event tables

#### 2. **Lateral MOvement Analysis**
Ques: Trace a "Kill Chain" where a compromised device moves laterally via network flow to a victim server; which subsequently accesses a critical resource.

Query to give a list of potential lateral movement kill chains:
```cypher
MATCH (attacker:Device)-[flow:NetworkFlow]->(victim:Device)
MATCH (victim)-[access:AccessedResource]->(target:Resource)
WHERE target.criticality IN ['critical', 'high']
  //time causality: the lateral move happened BEFORE the resource access
  AND flow.timestamp < access.timestamp
RETURN 
  attacker.hostname AS Source_Device, 
  victim.hostname AS Victim_Device, 
  target.name AS Exposed_Resource, 
  flow.timestamp AS Breach_Time
ORDER BY flow.timestamp DESC
```
Query to visualize the actual kill paths:
```cypher
MATCH path = (attacker:Device)-[flow:NetworkFlow]->(victim:Device)-[access:AccessedResource]->(target:Resource)
WHERE target.criticality IN ['critical', 'high']
  //ensure we aren't catching self-loops (internal processing)
  AND attacker <> victim
  //time causality
  AND flow.timestamp < access.timestamp
RETURN path
LIMIT 20
```
* SQL Pain Point: (Optimization failure)
    * Modeling the `Device A → Device B → Resource` hop requires complex Self-Joins or Recursive CTEs, which are notoriously difficult to write and scale
    * Correlating massive Network Flow tables with Access Logs based on time inequality `Flow_Time < Access_Time` prevents the database from using standard Hash Joins; often forcing slow full-table scans.

#### 3. **Priviledge Escalation Detection**
Ques: Identify any Non-Admin user who attempted to escalate their privileges to 'Admin' level on a device (specifically highlighting successful attempts)

```cypher
MATCH (u:User)-[esc:EscalatedPrivilege]->(d:Device)
WHERE u.is_admin = false
  AND esc.outcome = 'success' //or remove this line to see 'failure' attempts too
RETURN 
  u.username AS Suspicious_User, 
  esc.escalation_type AS Attack_Method, 
  d.hostname AS Target_Device, 
  esc.outcome AS Result
```
* SQL Pain Point (contextual blindness): 
+   * SQL forces expensive repeated JOINs between massive Event logs and User tables just to verify basic permissions (e.g: Is this actor an Admin?)
* In a graph, the User node intrinsically carries its role/state; which allows instant filtering without the computational overhead of connecting disparate tables

---
### **Steps for Local setup and Replication**
> Pre-req: **Docker Desktop** has to installed and running on your system

1. Clone this repo
```bash
git clone https://github.com/yeshapan/supply-chain-demo.git
cd supply-chain-demo
```
2. Launch the stack
```
docker-compose up
```
3. Access the dashboard
   * Wait for engine to boot + schema to load
   * Open browser to: `http://localhost:8081`
   * Login credentials to PuppyGraph UI:
       * username: puppygraph
       * password: puppygraph123
   
4. Run queries!! 🥳
---
### Repo structure
```bash
supply-chain-demo/
├── data/                       #raw CSV source files for all entities
├── sql/
│   └── init.sql                #SQL script for table creation + import CSV data into Postgres
├── assets/                     #contains image of graph schema generated by PuppyGraph
├── docker-compose.yml          #orchestrates the Postgres and PuppyGraph services
├── schema.json                 #complete graph mapping configuration for PuppyGraph   
└── README.md                   #some project documentation
```