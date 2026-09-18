interface CypherResult {
  Values: unknown[];
  Keys: string[];
}

interface SecurityGraphNode {
  id: string;
  type: 'cve' | 'instance' | 'public_instance' | 'lateral_target' | 'network' | 'subnet' | 'external' | 'vulnerability' | 'more' | 'external_combined';
  label: string;
  severity?: 'critical' | 'high' | 'medium' | 'low';
  details?: string;
  isMore?: boolean;
  moreType?: string;
  externalIps?: string[];
  isExpanded?: boolean;
}

interface SecurityGraphLink {
  source: string;
  target: string;
  type: 'exploits' | 'communicates' | 'accesses' | 'lateral_movement';
  label: string;
}

type SecurityViewType = 
  | 'cve_impact'
  | 'lateral_movement'
  | 'public_network_access'
  | 'network_security'
  | 'infrastructure_map'
  | 'default';

interface SecurityGraphResult {
  nodes: SecurityGraphNode[];
  links: SecurityGraphLink[];
  query?: string;
  viewType?: SecurityViewType;
}

class PuppyGraphService {
  private baseUrl = '/api/puppygraph';
  private username = 'puppygraph';
  private password = 'puppygraph123';

  private async executeCypher(query: string): Promise<CypherResult[]> {
    const response = await fetch(`${this.baseUrl}/submitCypher`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${btoa(`${this.username}:${this.password}`)}`,
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return Array.isArray(data) ? data : [data];
  }

  async getDashboardStats() {
    const queries = [
      {
        key: 'criticalCves',
        query: 'MATCH (cve:CVE) WHERE cve.base_score >= 7.0 RETURN count(cve) as count'
      },
      {
        key: 'securityFindings',
        query: 'MATCH (f:AWSInspectorFinding) RETURN count(f) as count'
      },
      {
        key: 'ec2Instances',
        query: 'MATCH (ec2:EC2Instance) RETURN count(ec2) as count'
      },
      {
        key: 'networkFlows',
        query: 'MATCH ()-[r:TRAFFIC_TO_EXTERNAL]->() RETURN count(r) as count'
      }
    ];

    const results = await Promise.all(
      queries.map(async ({ key, query }) => {
        try {
          const result = await this.executeCypher(query);
          return { key, value: result[0]?.Values[0] || 0 };
        } catch (error) {
          console.error(`Error executing query for ${key}:`, error);
          return { key, value: 0 };
        }
      })
    );

    const stats = {
      criticalCves: 0,
      securityFindings: 0,
      ec2Instances: 0,
      networkFlows: 0
    };
    
    results.forEach(({ key, value }) => {
      if (key === 'criticalCves') {
        stats.criticalCves = Number(value || 0);
      } else if (key === 'securityFindings') {
        stats.securityFindings = Number(value || 0);
      } else if (key === 'ec2Instances') {
        stats.ec2Instances = Number(value || 0);
      } else if (key === 'networkFlows') {
        stats.networkFlows = Number(value || 0);
      }
    });
    
    return stats;
  }

  async getRecentAlerts() {
    const query = `
      MATCH (ec2:EC2Instance)-[:HAS_FINDING]->(finding:AWSInspectorFinding)-[:HAS_VULNERABILITY]->(cve:CVE)
      WHERE cve.base_score >= 7.0
      RETURN ec2.instance_id as instance, cve.cve_id as cve, cve.base_score as score, finding.title as finding_title
      ORDER BY cve.base_score DESC
      LIMIT 10
    `;

    try {
      const results = await this.executeCypher(query);
      return results.map(result => ({
        instance: String(result.Values[0] || 'Unknown'),
        cve: String(result.Values[1] || 'Unknown'),
        score: Number(result.Values[2] || 0),
        title: String(result.Values[3] || 'Unknown')
      }));
    } catch (error) {
      console.error('Error fetching recent alerts:', error);
      return [];
    }
  }

  async getSuspiciousTraffic() {
    const query = `
      MATCH (ni:NetworkInterface)-[r:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
      WHERE ext.is_known_malicious = true
      RETURN ni.id as interface_id, ext.ip_address as external_ip, r.dstport as port
      LIMIT 10
    `;

    try {
      const results = await this.executeCypher(query);
      return results.map(result => ({
        interfaceId: String(result.Values[0] || 'Unknown'),
        externalIp: String(result.Values[1] || 'Unknown'),
        port: Number(result.Values[2] || 0)
      }));
    } catch (error) {
      console.error('Error fetching suspicious traffic:', error);
      return [];
    }
  }

  async getCVEData() {
    const query = `
      MATCH (cve:CVE)-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)-[:HAS_FINDING]-(ec2:EC2Instance)
      RETURN cve.id as cve_id, cve.base_score as score, cve.description_en as description, 
             count(DISTINCT ec2) as affected_instances
      ORDER BY cve.base_score DESC, count(DISTINCT ec2) DESC
      LIMIT 50
    `;

    try {
      const results = await this.executeCypher(query);
      return results.map(result => {
        const data: Record<string, unknown> = {};
        result.Keys.forEach((key, index) => {
          data[key] = result.Values[index];
        });
        
        return {
          id: String(data.cve_id || 'Unknown'),
          score: Number(data.score || 0),
          description: String(data.description || 'No description available'),
          affectedInstances: Number(data.affected_instances || 0),
          severity: this.getScoreSeverity(Number(data.score || 0)),
          status: 'Open'
        };
      });
    } catch (error) {
      console.error('Error fetching CVE data:', error);
      return [];
    }
  }

  private getScoreSeverity(score: number): string {
    if (score >= 9.0) return 'Critical';
    if (score >= 7.0) return 'High';
    if (score >= 4.0) return 'Medium';
    return 'Low';
  }

  async getCVEDetails(cveId: string) {
    // First, get basic CVE info
    const cveInfoQuery = `
      MATCH (cve:CVE {id: "${cveId}"})
      RETURN cve.id as id, cve.base_score as score, cve.base_severity as severity,
             cve.description_en as description, cve.vector_string as vector_string,
             cve.published as published, cve.last_modified as last_modified,
             cve.weaknesses as weaknesses, cve.reference_urls as references
    `;

    try {
      const cveInfoResult = await this.executeCypher(cveInfoQuery);
      
      if (cveInfoResult.length === 0) {
        return null;
      }

      const cveInfo = cveInfoResult[0];
      const cveData: Record<string, unknown> = {};
      cveInfo.Keys.forEach((key: string, index: number) => {
        cveData[key] = cveInfo.Values[index];
      });

      return {
        id: String(cveData.id || cveId),
        score: Number(cveData.score || 0),
        severity: String(cveData.severity || this.getScoreSeverity(Number(cveData.score || 0))),
        description: String(cveData.description || 'No description available'),
        vectorString: String(cveData.vector_string || 'N/A'),
        publishedDate: cveData.published ? new Date(String(cveData.published)).toLocaleDateString() : 'Unknown',
        lastModified: cveData.last_modified ? new Date(String(cveData.last_modified)).toLocaleDateString() : 'Unknown',
        weaknesses: cveData.weaknesses ? String(cveData.weaknesses).split(',').map((w: string) => w.trim()) : [],
        references: cveData.references ? String(cveData.references).split(',').map((r: string) => r.trim()) : []
      };
    } catch (error) {
      console.error('Error fetching CVE details:', error);
      return null;
    }
  }

  async getCVEAffectedInstances(cveId: string) {
    const query = `
      MATCH (cve:CVE {id: "${cveId}"})-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)-[:HAS_FINDING]-(ec2:EC2Instance)
      OPTIONAL MATCH (ec2)-[:HAS_NETWORK_INTERFACE]->(ni:NetworkInterface)-[:PART_OF_SUBNET]->(subnet:EC2Subnet)
      RETURN ec2.id as instance_id, finding.title as finding_title, 
             subnet.id as subnet_id, 'vpc-unknown' as vpc_id
      LIMIT 50
    `;

    try {
      const results = await this.executeCypher(query);
      return results.map((result: CypherResult) => {
        const data: Record<string, unknown> = {};
        result.Keys.forEach((key: string, index: number) => {
          data[key] = result.Values[index];
        });
        return {
          instanceId: String(data.instance_id || 'Unknown'),
          findingTitle: String(data.finding_title || 'Unknown'),
          subnetId: String(data.subnet_id || 'Unknown'),
          vpcId: String(data.vpc_id || 'Unknown')
        };
      });
    } catch (error) {
      console.error('Error fetching affected instances:', error);
      return [];
    }
  }

  async getCVENetworkConnections(cveId: string) {
    const query = `
      MATCH (cve:CVE {id: "${cveId}"})-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)-[:HAS_FINDING]-(ec2:EC2Instance)
      MATCH (ec2)-[:HAS_NETWORK_INTERFACE]->(ni:NetworkInterface)-[:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
      RETURN ni.id as interface_id, ext.ip_address as external_ip,
             ext.is_known_malicious as is_malicious
      LIMIT 20
    `;

    try {
      const results = await this.executeCypher(query);
      return results.map((result: CypherResult) => {
        const data: Record<string, unknown> = {};
        result.Keys.forEach((key: string, index: number) => {
          data[key] = result.Values[index];
        });
        return {
          interfaceId: String(data.interface_id || 'Unknown'),
          externalIp: String(data.external_ip || 'Unknown'),
          port: 443, // Default port since not in flow data
          isMalicious: Boolean(data.is_malicious || data.is_known_malicious || false)
        };
      });
    } catch (error) {
      console.error('Error fetching network connections:', error);
      return [];
    }
  }

  async getCVERelatedFindings(cveId: string) {
    const query = `
      MATCH (cve:CVE {id: "${cveId}"})-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)
      RETURN finding.title as title, finding.severity as severity, 
             finding.package_name as package_name
      LIMIT 20
    `;

    try {
      const results = await this.executeCypher(query);
      return results.map((result: CypherResult) => {
        const data: Record<string, unknown> = {};
        result.Keys.forEach((key: string, index: number) => {
          data[key] = result.Values[index];
        });
        return {
          title: String(data.title || 'Unknown'),
          severity: String(data.severity || 'Unknown'),
          packageName: String(data.package_name || '')
        };
      });
    } catch (error) {
      console.error('Error fetching related findings:', error);
      return [];
    }
  }

  async getCVEPublicNetworkGraph(cveId: string): Promise<SecurityGraphResult> {
    // Create a simplified graph showing only CVE -> Instances with external access
    try {
      const nodes: SecurityGraphNode[] = [];
      const links: SecurityGraphLink[] = [];
      const nodeIds = new Set<string>();
      const MAX_INSTANCES = 15; // Limit instances for readability

      // Helper function to get property by key name from Cypher result
      const getPropertyByKey = (result: CypherResult, keyName: string): unknown => {
        const keyIndex = result.Keys.indexOf(keyName);
        return keyIndex >= 0 ? result.Values[keyIndex] : null;
      };

      // Get CVE node (starting point)
      const cveQuery = `
        MATCH (cve:CVE {id: "${cveId}"})
        RETURN cve.id as id, cve.base_score as score, cve.description_en as description
      `;
      
      const cveResults = await this.executeCypher(cveQuery);
      if (cveResults.length === 0) {
        return { nodes: [], links: [] };
      }
      
      const cveData = cveResults[0];
      const cveNodeId = String(getPropertyByKey(cveData, 'id') || cveId);
      const score = Number(getPropertyByKey(cveData, 'score') || 0);
      const description = String(getPropertyByKey(cveData, 'description') || '');
      
      let severity: 'critical' | 'high' | 'medium' | 'low' = 'low';
      if (score >= 9.0) severity = 'critical';
      else if (score >= 7.0) severity = 'high';
      else if (score >= 4.0) severity = 'medium';
      
      nodes.push({
        id: cveNodeId,
        type: 'cve',
        label: cveNodeId,
        severity: severity,
        details: `CVSS Score: ${score} - ${description.substring(0, 100)}...`
      });
      nodeIds.add(cveNodeId);

      // Get instances affected by this CVE that have external network access
      const publicInstancesQuery = `
        MATCH (cve:CVE {id: "${cveId}"})-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)-[:HAS_FINDING]-(ec2:EC2Instance)
        MATCH (ec2)-[:HAS_NETWORK_INTERFACE]->(ni:NetworkInterface)-[:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
        WITH ec2, collect(ext.ip_address) as external_ips, collect(ext.is_known_malicious) as malicious_flags, count(ext) as external_count
        RETURN ec2.id as instance_id, external_ips, malicious_flags, external_count
        LIMIT ${MAX_INSTANCES + 2}
      `;
      
      const instanceResults = await this.executeCypher(publicInstancesQuery);
      const instancesToProcess = instanceResults.slice(0, MAX_INSTANCES);
      
      instancesToProcess.forEach(result => {
        const instanceRawId = String(getPropertyByKey(result, 'instance_id') || '');
        const externalIps = getPropertyByKey(result, 'external_ips') as string[] || [];
        const maliciousFlags = getPropertyByKey(result, 'malicious_flags') as boolean[] || [];
        const externalCount = Number(getPropertyByKey(result, 'external_count') || 0);
        
        const instanceId = `instance-${instanceRawId}`;
        const hasMaliciousTraffic = maliciousFlags.some(flag => flag === true);
        
        // Add instance node
        nodes.push({
          id: instanceId,
          type: 'instance',
          label: instanceRawId || 'Instance',
          severity: hasMaliciousTraffic ? 'critical' : 'medium',
          details: `EC2 Instance: ${instanceRawId}\nExternal Connections: ${externalCount}\n${hasMaliciousTraffic ? 'Has malicious traffic!' : 'Clean traffic only'}`
        });
        nodeIds.add(instanceId);
        
        // Add CVE -> Instance link
        links.push({
          source: cveNodeId,
          target: instanceId,
          type: 'exploits',
          label: 'Affects'
        });

        // Add all external IP nodes (no limit since they will be combined)
        externalIps.forEach((ip, index) => {
          const externalId = `external-${ip}`;
          const isMalicious = maliciousFlags[index] === true;
          
          if (!nodeIds.has(externalId)) {
            nodes.push({
              id: externalId,
              type: 'external',
              label: ip,
              severity: isMalicious ? 'critical' : 'low',
              details: `External IP: ${ip}${isMalicious ? ' (Malicious)' : ' (Clean)'}`
            });
            nodeIds.add(externalId);
          }
          
          // Add Instance -> External link
          links.push({
            source: instanceId,
            target: externalId,
            type: 'communicates',
            label: 'External Traffic'
          });
        });

        // No "more..." node needed for external IPs since they will be combined
      });
      
      // Add "more..." node for instances if needed
      if (instanceResults.length > MAX_INSTANCES) {
        const moreInstanceId = `more-instances-${cveId}`;
        nodes.push({
          id: moreInstanceId,
          type: 'more',
          label: `+${instanceResults.length - MAX_INSTANCES} more`,
          isMore: true,
          moreType: 'instance',
          details: `${instanceResults.length - MAX_INSTANCES} additional instances with external access`
        });
        nodeIds.add(moreInstanceId);
        
        links.push({
          source: cveNodeId,
          target: moreInstanceId,
          type: 'exploits',
          label: 'More Instances'
        });
      }

      const displayQuery = `-- Public Network Access View for ${cveId}
MATCH (cve:CVE {id: "${cveId}"})-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)-[:HAS_FINDING]-(ec2:EC2Instance)
MATCH (ec2)-[:HAS_NETWORK_INTERFACE]->(ni:NetworkInterface)-[:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
WITH ec2, collect(ext.ip_address) as external_ips, count(ext) as external_count
RETURN ec2.id as instance_id, external_ips, external_count
LIMIT ${MAX_INSTANCES + 2}`;

      return { nodes, links, query: displayQuery, viewType: 'public_network_access' };
    } catch (error) {
      console.error('Error fetching CVE public network graph:', error);
      return { nodes: [], links: [], viewType: 'public_network_access' };
    }
  }

  async getCVELateralMovementGraph(cveId: string): Promise<SecurityGraphResult> {
    // Create a simplified graph showing lateral movement risk through step-by-step queries
    try {
      const nodes: SecurityGraphNode[] = [];
      const links: SecurityGraphLink[] = [];
      const nodeIds = new Set<string>();

      // Helper function to get property by key name from Cypher result
      const getPropertyByKey = (result: CypherResult, keyName: string): unknown => {
        const keyIndex = result.Keys.indexOf(keyName);
        return keyIndex >= 0 ? result.Values[keyIndex] : null;
      };

      // Step 1: Get CVE node (starting point)
      const cveQuery = `
        MATCH (cve:CVE {id: "${cveId}"})
        RETURN cve.id as id, cve.base_score as score, cve.description_en as description
      `;
      
      const cveResults = await this.executeCypher(cveQuery);
      if (cveResults.length === 0) {
        console.log(`No CVE found with id: ${cveId}`);
        return { nodes: [], links: [] };
      }
      
      const cveData = cveResults[0];
      const cveNodeId = String(getPropertyByKey(cveData, 'id') || cveId);
      const score = Number(getPropertyByKey(cveData, 'score') || 0);
      const description = String(getPropertyByKey(cveData, 'description') || '');
      
      let severity: 'critical' | 'high' | 'medium' | 'low' = 'low';
      if (score >= 9.0) severity = 'critical';
      else if (score >= 7.0) severity = 'high';
      else if (score >= 4.0) severity = 'medium';
      
      nodes.push({
        id: cveNodeId,
        type: 'cve',
        label: cveNodeId,
        severity: severity,
        details: `CVSS Score: ${score} - ${description.substring(0, 100)}...`
      });
      nodeIds.add(cveNodeId);

      // Step 2: Get all instances affected by this CVE (simplified)
      const affectedInstancesQuery = `
        MATCH (cve:CVE {id: "${cveId}"})-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)-[:HAS_FINDING]-(ec2:EC2Instance)
        RETURN DISTINCT ec2.id as instance_id
      `;
      
      const affectedResults = await this.executeCypher(affectedInstancesQuery);
      console.log(`Found ${affectedResults.length} instances affected by ${cveId}`);
      
      const affectedInstanceIds = new Set<string>();
      
      // Store affected instances but don't add them to the graph yet
      // We'll only add them if they become public instances or lateral targets
      affectedResults.forEach(result => {
        const instanceRawId = String(getPropertyByKey(result, 'instance_id') || '');
        affectedInstanceIds.add(instanceRawId);
      });

      // Step 3: Check which affected instances have external access (potential entry points)
      if (affectedInstanceIds.size > 0) {
        const instanceIdsList = Array.from(affectedInstanceIds).map(id => `"${id}"`).join(', ');
        
        const publicAccessQuery = `
          MATCH (ec2:EC2Instance)-[:HAS_NETWORK_INTERFACE]->(ni:NetworkInterface)-[:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
          WHERE ec2.id IN [${instanceIdsList}]
          WITH ec2, collect(ext.ip_address) as sample_external_ips, count(ext) as external_count
          RETURN ec2.id as instance_id, external_count, sample_external_ips
        `;
        
        const publicResults = await this.executeCypher(publicAccessQuery);
        console.log(`Found ${publicResults.length} affected instances with external access`);
        
        const publicInstanceIds = new Set<string>();
        
        // Update affected instances that have public access
        publicResults.forEach(result => {
          const instanceRawId = String(getPropertyByKey(result, 'instance_id') || '');
          const externalCount = Number(getPropertyByKey(result, 'external_count') || 0);
          const sampleIps = getPropertyByKey(result, 'sample_external_ips') as string[] || [];
          
          const instanceId = `instance-${instanceRawId}`;
          publicInstanceIds.add(instanceRawId);
          
          // Add public instance node
          nodes.push({
            id: instanceId,
            type: 'public_instance',
            label: `${instanceRawId} (Public, Affected)`,
            severity: 'critical',
            details: `CVE-affected Public Instance: ${instanceRawId}\nExternal Connections: ${externalCount}\nEntry point for lateral movement!`
          });
          nodeIds.add(instanceId);
          
          // Add CVE -> Public Instance link
          links.push({
            source: cveNodeId,
            target: instanceId,
            type: 'exploits',
            label: 'Affects'
          });
          
          // Add all external IPs
          const allIps = Array.isArray(sampleIps) ? sampleIps : [];
          allIps.forEach((ip) => {
            const externalId = `external-${ip}`;
            if (!nodeIds.has(externalId)) {
              nodes.push({
                id: externalId,
                type: 'external',
                label: ip,
                severity: 'low',
                details: `External IP: ${ip}`
              });
              nodeIds.add(externalId);
              
              links.push({
                source: instanceId,
                target: externalId,
                type: 'communicates',
                label: 'External Access'
              });
            }
          });
        });
        
        // Step 4: Find instances that can communicate with affected public instances
        if (publicInstanceIds.size > 0) {
          const publicIdsList = Array.from(publicInstanceIds).map(id => `"${id}"`).join(', ');
          
          const lateralMovementQuery = `
            MATCH (publicEc2:EC2Instance)-[:HAS_NETWORK_INTERFACE]->(publicNi:NetworkInterface)
            WHERE publicEc2.id IN [${publicIdsList}]
            MATCH (publicNi)-[:TRAFFIC_BETWEEN_INTERFACES]-(targetNi:NetworkInterface)<-[:HAS_NETWORK_INTERFACE]-(targetEc2:EC2Instance)
            WHERE targetEc2.id <> publicEc2.id
            RETURN DISTINCT targetEc2.id as instance_id, publicEc2.id as connected_public_instance
            LIMIT 10
          `;
          
          const lateralResults = await this.executeCypher(lateralMovementQuery);
          console.log(`Found ${lateralResults.length} instances connected to affected public instances`);
          
          // Add lateral movement targets
          const processedTargets = new Set<string>();
          lateralResults.forEach(result => {
            const instanceRawId = String(getPropertyByKey(result, 'instance_id') || '');
            const connectedPublicId = String(getPropertyByKey(result, 'connected_public_instance') || '');
            
            const instanceId = `instance-${instanceRawId}`;
            
            if (!nodeIds.has(instanceId) && !processedTargets.has(instanceRawId)) {
              processedTargets.add(instanceRawId);
              
              nodes.push({
                id: instanceId,
                type: 'lateral_target',
                label: `${instanceRawId} (Clean)`,
                severity: 'low',
                details: `Clean Instance: ${instanceRawId}\nPotential lateral movement target`
              });
              nodeIds.add(instanceId);
            }
            
            // Add lateral movement connection
            const publicNodeId = `instance-${connectedPublicId}`;
            if (nodeIds.has(publicNodeId) && nodeIds.has(instanceId)) {
              links.push({
                source: publicNodeId,
                target: instanceId,
                type: 'lateral_movement',
                label: 'Lateral Path'
              });
            }
          });
        }
      }

      const displayQuery = `-- Lateral Movement Analysis for ${cveId}
-- Step 1: Find CVE-affected instances
MATCH (cve:CVE {id: "${cveId}"})-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)-[:HAS_FINDING]-(ec2:EC2Instance)
RETURN ec2.id as affected_instance

-- Step 2: Find which affected instances have external access
MATCH (ec2:EC2Instance)-[:HAS_NETWORK_INTERFACE]->(ni:NetworkInterface)-[:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
WHERE ec2.id IN [affected_instances]
RETURN ec2.id as public_affected_instance

-- Step 3: Find instances connected to affected public instances  
MATCH (targetEc2:EC2Instance)-[:HAS_NETWORK_INTERFACE]->(targetNi:NetworkInterface)
MATCH (publicEc2:EC2Instance)-[:HAS_NETWORK_INTERFACE]->(publicNi:NetworkInterface)
WHERE publicEc2.id IN [public_affected_instances]
MATCH (targetNi)-[:TRAFFIC_BETWEEN_INTERFACES]-(publicNi)
RETURN targetEc2.id as lateral_movement_target`;

      console.log(`Generated lateral movement graph with ${nodes.length} nodes and ${links.length} links`);
      return { nodes, links, query: displayQuery, viewType: 'lateral_movement' };
    } catch (error) {
      console.error('Error fetching CVE lateral movement graph:', error);
      return { nodes: [], links: [], viewType: 'lateral_movement' };
    }
  }

  async getCVESecurityGraph(cveId: string): Promise<SecurityGraphResult> {
    // Progressive layer-based graph building using one-hop queries from previous layer results
    try {
      const nodes: SecurityGraphNode[] = [];
      const links: SecurityGraphLink[] = [];
      const nodeIds = new Set<string>();
      const MAX_LAYER_ITEMS = 9;
      const QUERY_LIMIT = 10;

      // Helper function to get property by key name from Cypher result
      const getPropertyByKey = (result: CypherResult, keyName: string): unknown => {
        const keyIndex = result.Keys.indexOf(keyName);
        return keyIndex >= 0 ? result.Values[keyIndex] : null;
      };

      // Layer 1: Get CVE node (starting point)
      const cveQuery = `
        MATCH (cve:CVE {id: "${cveId}"})
        RETURN cve.id as id, cve.base_score as score, cve.description_en as description
      `;
      
      const cveResults = await this.executeCypher(cveQuery);
      if (cveResults.length === 0) {
        return { nodes: [], links: [] };
      }
      
      const cveData = cveResults[0];
      const cveNodeId = String(getPropertyByKey(cveData, 'id') || cveId);
      const score = Number(getPropertyByKey(cveData, 'score') || 0);
      const description = String(getPropertyByKey(cveData, 'description') || '');
      
      let severity: 'critical' | 'high' | 'medium' | 'low' = 'low';
      if (score >= 9.0) severity = 'critical';
      else if (score >= 7.0) severity = 'high';
      else if (score >= 4.0) severity = 'medium';
      
      nodes.push({
        id: cveNodeId,
        type: 'cve',
        label: cveNodeId,
        severity: severity,
        details: `CVSS Score: ${score} - ${description.substring(0, 100)}...`
      });
      nodeIds.add(cveNodeId);

      // Layer 2: One hop from CVE -> Findings
      const findingsQuery = `
        MATCH (cve:CVE {id: "${cveId}"})-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)
        RETURN finding.id as id, finding.title as title, finding.severity as severity
        LIMIT ${QUERY_LIMIT}
      `;
      
      const findingResults = await this.executeCypher(findingsQuery);
      const findingsToProcess = findingResults.slice(0, MAX_LAYER_ITEMS);
      const processedFindingIds: string[] = [];
      
      findingsToProcess.forEach(result => {
        const findingRawId = String(getPropertyByKey(result, 'id') || '');
        const findingTitle = String(getPropertyByKey(result, 'title') || 'Finding');
        const findingSeverity = String(getPropertyByKey(result, 'severity') || 'low').toLowerCase();
        
        const findingId = `finding-${findingRawId}`;
        
        nodes.push({
          id: findingId,
          type: 'vulnerability',
          label: findingTitle.substring(0, 20) + '...',
          severity: findingSeverity as 'critical' | 'high' | 'medium' | 'low',
          details: findingTitle
        });
        nodeIds.add(findingId);
        processedFindingIds.push(findingRawId);
        
        // Add CVE -> Finding link
        links.push({
          source: cveNodeId,
          target: findingId,
          type: 'exploits',
          label: 'Exploits'
        });
      });
      
      // Add "more..." node for findings if needed
      if (findingResults.length > MAX_LAYER_ITEMS) {
        const moreNodeId = `more-vulnerability-${cveId}`;
        nodes.push({
          id: moreNodeId,
          type: 'more',
          label: 'more...',
          isMore: true,
          moreType: 'vulnerability',
          details: 'More vulnerability findings available'
        });
        nodeIds.add(moreNodeId);
        
        links.push({
          source: cveNodeId,
          target: moreNodeId,
          type: 'exploits',
          label: 'More Findings'
        });
      }

      // Layer 3: One hop from Findings -> Instances (only if we have findings)
      if (processedFindingIds.length > 0) {
        const findingIdsList = processedFindingIds.map(id => `"${id}"`).join(', ');
        const instancesQuery = `
          MATCH (finding:AWSInspectorFinding)-[:HAS_FINDING]-(ec2:EC2Instance)
          WHERE finding.id IN [${findingIdsList}]
          RETURN DISTINCT finding.id as finding_id, ec2.id as instance_id
          LIMIT ${QUERY_LIMIT}
        `;
        
        const instanceResults = await this.executeCypher(instancesQuery);
        const instancesToProcess = instanceResults.slice(0, MAX_LAYER_ITEMS);
        const processedInstanceIds: string[] = [];
        
        instancesToProcess.forEach(result => {
          const findingRawId = String(getPropertyByKey(result, 'finding_id') || '');
          const instanceRawId = String(getPropertyByKey(result, 'instance_id') || '');
          
          const findingId = `finding-${findingRawId}`;
          const instanceId = `instance-${instanceRawId}`;
          
          // Add instance node if not exists
          if (!nodeIds.has(instanceId)) {
            nodes.push({
              id: instanceId,
              type: 'instance',
              label: instanceRawId || 'Instance',
              details: `EC2 Instance: ${instanceRawId}`
            });
            nodeIds.add(instanceId);
            processedInstanceIds.push(instanceRawId);
          }
          
          // Add Finding -> Instance link if both nodes exist
          if (nodeIds.has(findingId) && nodeIds.has(instanceId)) {
            links.push({
              source: findingId,
              target: instanceId,
              type: 'accesses',
              label: 'Affects'
            });
          }
        });
        
        // Add "more..." node for instances if needed
        if (instanceResults.length > MAX_LAYER_ITEMS) {
          const moreNodeId = `more-instance-${cveId}`;
          nodes.push({
            id: moreNodeId,
            type: 'more',
            label: 'more...',
            isMore: true,
            moreType: 'instance',
            details: 'More affected instances available'
          });
          nodeIds.add(moreNodeId);
        }

        // Layer 4: One hop from Instances -> Network Interfaces (only if we have instances)
        if (processedInstanceIds.length > 0) {
          const instanceIdsList = processedInstanceIds.map(id => `"${id}"`).join(', ');
          const networkQuery = `
            MATCH (ec2:EC2Instance)-[:HAS_NETWORK_INTERFACE]->(ni:NetworkInterface)
            WHERE ec2.id IN [${instanceIdsList}]
            RETURN DISTINCT ec2.id as instance_id, ni.id as network_id
            LIMIT ${QUERY_LIMIT}
          `;
          
          const networkResults = await this.executeCypher(networkQuery);
          const networksToProcess = networkResults.slice(0, MAX_LAYER_ITEMS);
          const processedNetworkIds: string[] = [];
          
          networksToProcess.forEach(result => {
            const instanceRawId = String(getPropertyByKey(result, 'instance_id') || '');
            const networkRawId = String(getPropertyByKey(result, 'network_id') || '');
            
            const instanceId = `instance-${instanceRawId}`;
            const networkId = `network-${networkRawId}`;
            
            // Add network node if instance exists and network node doesn't exist
            if (nodeIds.has(instanceId) && !nodeIds.has(networkId)) {
              nodes.push({
                id: networkId,
                type: 'network',
                label: `NI-${networkRawId.substring(0, 8)}`,
                details: `Network Interface: ${networkRawId}`
              });
              nodeIds.add(networkId);
              processedNetworkIds.push(networkRawId);
            }
            
            // Add Instance -> Network link if both nodes exist
            if (nodeIds.has(instanceId) && nodeIds.has(networkId)) {
              links.push({
                source: instanceId,
                target: networkId,
                type: 'communicates',
                label: 'Network Access'
              });
            }
          });
          
          // Add "more..." node for networks if needed
          if (networkResults.length > MAX_LAYER_ITEMS) {
            const moreNodeId = `more-network-${cveId}`;
            nodes.push({
              id: moreNodeId,
              type: 'more',
              label: 'more...',
              isMore: true,
              moreType: 'network',
              details: 'More network interfaces available'
            });
            nodeIds.add(moreNodeId);
          }

          // Layer 5: One hop from Network Interfaces -> External IPs (only if we have networks)
          if (processedNetworkIds.length > 0) {
            const networkIdsList = processedNetworkIds.map(id => `"${id}"`).join(', ');
            const externalQuery = `
              MATCH (ni:NetworkInterface)-[:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
              WHERE ni.id IN [${networkIdsList}]
              RETURN DISTINCT ni.id as network_id, ext.ip_address as ip_address, ext.is_known_malicious as is_known_malicious
              LIMIT ${QUERY_LIMIT}
            `;
            
            const externalResults = await this.executeCypher(externalQuery);
            // Process all external results since they will be combined
            
            externalResults.forEach(result => {
              const networkRawId = String(getPropertyByKey(result, 'network_id') || '');
              const externalIp = String(getPropertyByKey(result, 'ip_address') || '');
              const isMalicious = Boolean(getPropertyByKey(result, 'is_known_malicious') || false);
              
              const networkId = `network-${networkRawId}`;
              const externalId = `external-${externalIp}`;
              
              // Add external node if network exists and external node doesn't exist
              if (nodeIds.has(networkId) && !nodeIds.has(externalId)) {
                nodes.push({
                  id: externalId,
                  type: 'external',
                  label: externalIp,
                  severity: isMalicious ? 'critical' : 'low',
                  details: `External IP: ${externalIp}${isMalicious ? ' (Malicious)' : ' (Clean)'}`
                });
                nodeIds.add(externalId);
              }
              
              // Add Network -> External link if both nodes exist
              if (nodeIds.has(networkId) && nodeIds.has(externalId)) {
                links.push({
                  source: networkId,
                  target: externalId,
                  type: 'communicates',
                  label: 'External Traffic'
                });
              }
            });
            
            // No "more..." node needed for external IPs since they will be combined
          }
        }
      }

      // Filter out any links that reference non-existent nodes (safety check)
      const validLinks = links.filter(link => {
        const sourceId = typeof link.source === 'string' ? link.source : (link.source as SecurityGraphNode).id;
        const targetId = typeof link.target === 'string' ? link.target : (link.target as SecurityGraphNode).id;
        return nodeIds.has(sourceId) && nodeIds.has(targetId);
      });

      const displayQuery = `-- Default Progressive View for ${cveId}
-- Layer 1: CVE
MATCH (cve:CVE {id: "${cveId}"})
RETURN cve.id as id, cve.base_score as score, cve.description_en as description

-- Layer 2: CVE -> Findings
MATCH (cve:CVE {id: "${cveId}"})-[:HAS_VULNERABILITY]-(finding:AWSInspectorFinding)
RETURN finding.id, finding.title, finding.severity

-- Layer 3: Findings -> Instances
MATCH (finding:AWSInspectorFinding)-[:HAS_FINDING]-(ec2:EC2Instance)
WHERE finding.id IN [finding_ids]
RETURN finding.id as finding_id, ec2.id as instance_id

-- Layer 4: Instances -> Network Interfaces
MATCH (ec2:EC2Instance)-[:HAS_NETWORK_INTERFACE]->(ni:NetworkInterface)
WHERE ec2.id IN [instance_ids]
RETURN ec2.id as instance_id, ni.id as network_id

-- Layer 5: Network Interfaces -> External IPs
MATCH (ni:NetworkInterface)-[:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
WHERE ni.id IN [network_ids]
RETURN ni.id as network_id, ext.ip_address, ext.is_known_malicious`;

      return { nodes, links: validLinks, query: displayQuery, viewType: 'cve_impact' };
    } catch (error) {
      console.error('Error fetching CVE security graph:', error);
      return { nodes: [], links: [], viewType: 'cve_impact' };
    }
  }


  async getNetworkAnalysisData() {
    const queries = [
      {
        key: 'topExternalConnections',
        query: `
          MATCH (ni:NetworkInterface)-[r:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
          RETURN ext.ip_address as ip, ext.is_known_malicious as is_malicious, count(r) as connection_count
          ORDER BY connection_count DESC
          LIMIT 10
        `
      },
      {
        key: 'suspiciousInstances',
        query: `
          MATCH (ec2:EC2Instance)-[:HAS_NETWORK_INTERFACE]->(ni:NetworkInterface)-[:TRAFFIC_TO_EXTERNAL]->(ext:ExternalIPAddress)
          WHERE ext.is_known_malicious = true
          RETURN ec2.id as instance, count(DISTINCT ext) as malicious_connections
          ORDER BY malicious_connections DESC
          LIMIT 10
        `
      },
      {
        key: 'topPorts',
        query: `
          MATCH ()-[r:TRAFFIC_TO_EXTERNAL]->()
          RETURN r.port as port, count(r) as usage_count
          ORDER BY usage_count DESC
          LIMIT 10
        `
      }
    ];

    const results = await Promise.all(
      queries.map(async ({ key, query }) => {
        try {
          const result = await this.executeCypher(query);
          return { key, data: result };
        } catch (error) {
          console.error(`Error executing query for ${key}:`, error);
          return { key, data: [] };
        }
      })
    );

    return results.reduce((acc, { key, data }) => {
      acc[key] = data;
      return acc;
    }, {} as Record<string, CypherResult[]>);
  }
}

export const puppyGraphService = new PuppyGraphService();