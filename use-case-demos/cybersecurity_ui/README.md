#  Cybersecurity Graph Demo

## Summary
This demo showcases a comprehensive cybersecurity platform that includes:

1. Use Docker Compose to launch a PostgreSQL database and PuppyGraph
2. Upload the graph model (`schema.json`) into PuppyGraph  
3. Access an intuitive web-based cybersecurity dashboard for vulnerability management
4. Explore interactive security graph visualizations with multiple analysis views

## Project Structure

├── docker-compose.yaml  
├── postgres-init/  
│   ├── csv_data/  
│   ├── init.sql  
├── cybersecurity-dashboard/          # Next.js web application
│   ├── src/app/                      # Application pages
│   │   ├── page.tsx                  # Executive dashboard
│   │   ├── cve/                      # CVE analysis page
│   │   ├── findings/                 # Threat intelligence page
│   │   ├── network/                  # Network security page
│   │   ├── reports/                  # Compliance reports page
│   │   └── security-graph/           # Interactive security graph
│   ├── src/components/               # React components
│   │   ├── Layout/                   # Dashboard layout
│   │   ├── SecurityGraph.tsx         # Graph visualization component
│   │   └── CVEDetailsPanel.tsx       # CVE details component
│   └── src/services/                 # API services
│       └── puppygraph.ts            # PuppyGraph service integration
├── README.md  
└── schema.json

## Prerequisites:
- Docker
- Docker Compose


## Deployment
1. Start the Postgres services and PuppyGraph by running:
```bash
docker compose up -d
```
Example output:
```bash
[+] Running 3/3
✔ Network puppy-postgres        Created
✔ Container postgres            Started
✔ Container puppygraph          Started
✔ Container cybersecurity-ui    Started
```

2. Wait a few seconds for PostgreSQL to load the CSVs. Then open the PuppyGraph UI.

## Modeling the Graph
1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
- Username: `puppygraph`
- Password: `puppygraph123`

2. Upload the schema:
- Select the file `schema.json` in the Upload Graph Schema JSON section and click on Upload.

## Cybersecurity Demo Dashboard

The platform includes a comprehensive web-based dashboard accessible at **http://localhost:3000** after starting the dashboard services.

### Getting Started with the Demo Dashboard

Access the dashboard at **http://localhost:3000**

This is a demo dashboard that is connected to the PuppyGraph and the PostgreSQL database. It demonstrates how to use the PuppyGraph provided Cypher API to enable a rich set of security analytics and visualization. The demo UI is built with Next.js and Material UI.

The dashboard provides an executive-level security overview with the following key features:

### Dashboard Overview

The cybersecurity dashboard provides an executive-level security overview with the following key features:

#### **Executive Dashboard**
- **Real-time Security Metrics**: Critical CVE count, security findings, monitored EC2 instances, and VPC flow analysis
- **Recent Security Alerts**: Live feed of the latest CVE detections and suspicious network activity
- **Quick Actions**: Direct access to investigation workflows and compliance reporting

#### **Analytics & Intelligence**
- **Threat Intelligence**: Comprehensive view of AWS Inspector findings and vulnerability assessments
- **Executive Dashboard**: High-level security posture overview with actionable metrics

#### **Security Operations**

### Vulnerability Management

The **Vulnerability Management** section provides comprehensive CVE (Common Vulnerabilities and Exposures) investigation capabilities:

#### **CVE Investigation Features**
- **Vulnerability Database**: Complete catalog of CVEs affecting your infrastructure
- **Impact Assessment**: Detailed analysis of which instances and services are affected by specific vulnerabilities
- **Severity Prioritization**: Critical, High, Medium, and Low severity classification with CVSS scoring
- **Remediation Tracking**: Monitor vulnerability remediation progress across your environment

#### **Detailed CVE Analysis**
- **Affected Infrastructure**: Identify all EC2 instances, network interfaces, and subnets impacted by each CVE
- **Risk Assessment**: Understand the potential blast radius and attack surface exposure
- **Timeline Analysis**: Track when vulnerabilities were first detected and last observed
- **Compliance Impact**: Assess how CVEs affect regulatory compliance requirements

### Security Graph

The **Security Graph** provides advanced interactive visualization of cybersecurity relationships with **three distinct analysis views**:

#### **1. Default View - CVE Impact Analysis**
- **Purpose**: Visualize vulnerability exploitation paths and affected infrastructure components
- **Analysis Capabilities**:
  - Trace CVE propagation through security findings
  - Identify vulnerable instances and network exposure
  - Assess potential blast radius of exploitation
  - Prioritize remediation based on connectivity
- **Use Case**: Understanding how a specific CVE affects your infrastructure and planning remediation efforts

#### **2. Public Network Access**
- **Purpose**: Identify instances with public network exposures that could be higher risk to certain attacks
- **Analysis Capabilities**:
  - Detect instances with direct internet connectivity
  - Assess log4shell attack vectors via LDAP server access
  - Identify remote code execution opportunities
  - Monitor public-facing services for exploitation risks
- **Use Case**: Analyzing attack vectors that require internet access, such as log4shell vulnerabilities requiring LDAP server communication

#### **3. Lateral Movement Risk**
- **Purpose**: Analyze network connectivity to understand attack risk if public accessible nodes are compromised
- **Analysis Capabilities**:
  - Map potential lateral movement from compromised public nodes
  - Identify internal systems reachable after initial breach
  - Assess network segmentation effectiveness against attacks
  - Evaluate blast radius of public node compromise
- **Use Case**: Understanding the potential impact if an internet-facing system is compromised and how attackers could move laterally through your network

## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
docker compose down --volumes --remove-orphans
```
