'use client';
import React, { useEffect, useState } from 'react';
import {
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
} from '@mui/material';
import DashboardLayout from '@/components/Layout/DashboardLayout';
import CVEDetailsPanel from '@/components/CVEDetailsPanel';
import { puppyGraphService } from '@/services/puppygraph';


const getSeverityColor = (severity: string): 'error' | 'warning' | 'info' | 'success' | 'default' => {
  switch (severity.toLowerCase()) {
    case 'critical': return 'error';
    case 'high': return 'warning';
    case 'medium': return 'info';
    case 'low': return 'success';
    default: return 'default';
  }
};

export default function CVEAnalysis() {
  const [loading, setLoading] = useState(true);
  const [cveData, setCveData] = useState<Array<{
    id: string;
    score: number;
    description: string;
    affectedInstances: number;
    severity: string;
    status: string;
  }>>([]);
  const [cveDetails, setCveDetails] = useState<{
    id: string;
    score: number;
    severity: string;
    description: string;
    vectorString: string;
    publishedDate: string;
    lastModified: string;
    weaknesses: string[];
    references: string[];
    affectedInstances?: Array<{
      instanceId: string;
      findingTitle: string;
      subnetId: string;
      vpcId: string;
    }>;
    networkConnections?: Array<{
      interfaceId: string;
      externalIp: string;
      port: number;
      isMalicious: boolean;
    }>;
    relatedFindings?: Array<{
      title: string;
      severity: string;
      packageName: string;
    }>;
    securityGraph?: {
      nodes: Array<{
        id: string;
        type: 'cve' | 'instance' | 'public_instance' | 'lateral_target' | 'network' | 'subnet' | 'external' | 'vulnerability' | 'more' | 'external_combined';
        label: string;
        severity?: 'critical' | 'high' | 'medium' | 'low';
        details?: string;
        isMore?: boolean;
        moreType?: string;
        externalIps?: string[];
        isExpanded?: boolean;
      }>;
      links: Array<{
        source: string;
        target: string;
        type: 'exploits' | 'communicates' | 'accesses' | 'lateral_movement';
        label: string;
      }>;
    };
  } | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [sectionLoading, setSectionLoading] = useState({
    affectedInstances: false,
    networkConnections: false,
    relatedFindings: false,
    securityGraph: false
  });
  const [panelOpen, setPanelOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await puppyGraphService.getCVEData();
        setCveData(data);
      } catch (error) {
        console.error('Error fetching CVE data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleRowClick = async (cveId: string) => {
    setPanelOpen(true);
    setDetailsLoading(true);
    setCveDetails(null);
    setSectionLoading({
      affectedInstances: false,
      networkConnections: false,
      relatedFindings: false,
      securityGraph: false
    });

    try {
      // First get basic CVE details
      const details = await puppyGraphService.getCVEDetails(cveId);
      setCveDetails(details);
      setDetailsLoading(false);

      if (details) {
        // Then load each section separately
        setSectionLoading(prev => ({ ...prev, affectedInstances: true }));
        const affectedInstances = await puppyGraphService.getCVEAffectedInstances(cveId);
        setCveDetails(prev => prev ? { ...prev, affectedInstances } : null);
        setSectionLoading(prev => ({ ...prev, affectedInstances: false }));

        setSectionLoading(prev => ({ ...prev, networkConnections: true }));
        const networkConnections = await puppyGraphService.getCVENetworkConnections(cveId);
        setCveDetails(prev => prev ? { ...prev, networkConnections } : null);
        setSectionLoading(prev => ({ ...prev, networkConnections: false }));

        setSectionLoading(prev => ({ ...prev, relatedFindings: true }));
        const relatedFindings = await puppyGraphService.getCVERelatedFindings(cveId);
        setCveDetails(prev => prev ? { ...prev, relatedFindings } : null);
        setSectionLoading(prev => ({ ...prev, relatedFindings: false }));

        // Load security graph data using Cypher query
        setSectionLoading(prev => ({ ...prev, securityGraph: true }));
        const securityGraph = await puppyGraphService.getCVESecurityGraph(cveId);
        setCveDetails(prev => prev ? { ...prev, securityGraph } : null);
        setSectionLoading(prev => ({ ...prev, securityGraph: false }));
      }
    } catch (error) {
      console.error('Error fetching CVE details:', error);
      setDetailsLoading(false);
      setSectionLoading({
        affectedInstances: false,
        networkConnections: false,
        relatedFindings: false,
        securityGraph: false
      });
    }
  };

  const handlePanelClose = () => {
    setPanelOpen(false);
    setCveDetails(null);
  };

  if (loading) {
    return (
      <DashboardLayout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Box>
        <Typography variant="h4" component="h1" gutterBottom>
          CVE Analysis
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
          Monitor and investigate Common Vulnerabilities and Exposures affecting your infrastructure
        </Typography>

        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>CVE ID</TableCell>
                  <TableCell>Severity</TableCell>
                  <TableCell>CVSS Score</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Affected Instances</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {cveData.map((cve) => (
                  <TableRow 
                    key={cve.id} 
                    hover 
                    onClick={() => handleRowClick(cve.id)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {cve.id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={cve.severity} 
                        color={getSeverityColor(cve.severity)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{cve.score}</TableCell>
                    <TableCell sx={{ maxWidth: 300 }}>
                      <Typography variant="body2" noWrap>
                        {cve.description}
                      </Typography>
                    </TableCell>
                    <TableCell>{cve.affectedInstances}</TableCell>
                    <TableCell>
                      <Chip 
                        label={cve.status} 
                        variant="outlined" 
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
        
        <CVEDetailsPanel
          open={panelOpen}
          onClose={handlePanelClose}
          cveDetails={cveDetails}
          loading={detailsLoading}
          sectionLoading={sectionLoading}
        />
      </Box>
    </DashboardLayout>
  );
}