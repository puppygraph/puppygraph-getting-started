'use client';
import React, { useEffect, useState, Suspense } from 'react';
import {
  Typography,
  Box,
  Paper,
  CircularProgress,
  Button,
  Chip,
  Card,
  CardContent,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import { ArrowBack, Security, AccountTree, Public, Hub } from '@mui/icons-material';
import { useSearchParams, useRouter } from 'next/navigation';
import DashboardLayout from '@/components/Layout/DashboardLayout';
import SecurityGraph from '@/components/SecurityGraph';
import { puppyGraphService } from '@/services/puppygraph';

interface SecurityGraphData {
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
}

interface CVEInfo {
  id: string;
  score: number;
  severity: string;
  description: string;
}

const getSeverityColor = (severity: string): 'error' | 'warning' | 'info' | 'success' | 'default' => {
  switch (severity.toLowerCase()) {
    case 'critical': return 'error';
    case 'high': return 'warning';
    case 'medium': return 'info';
    case 'low': return 'success';
    default: return 'default';
  }
};

type GraphView = 'default' | 'public-network' | 'lateral-movement';

function SecurityGraphContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const cveId = searchParams.get('cve');

  const [loading, setLoading] = useState(true);
  const [viewLoading, setViewLoading] = useState(false);
  const [currentView, setCurrentView] = useState<GraphView>('default');
  const [cveInfo, setCveInfo] = useState<CVEInfo | null>(null);
  const [graphData, setGraphData] = useState<SecurityGraphData | null>(null);

  const fetchGraphData = async (view: GraphView) => {
    if (!cveId) return;

    try {
      setViewLoading(true);
      
      let graphResult;
      if (view === 'public-network') {
        graphResult = await puppyGraphService.getCVEPublicNetworkGraph(cveId);
      } else if (view === 'lateral-movement') {
        graphResult = await puppyGraphService.getCVELateralMovementGraph(cveId);
      } else {
        graphResult = await puppyGraphService.getCVESecurityGraph(cveId);
      }
      
      setGraphData(graphResult);
    } catch (error) {
      console.error('Error fetching graph data:', error);
    } finally {
      setViewLoading(false);
    }
  };

  useEffect(() => {
    const fetchInitialData = async () => {
      if (!cveId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        
        // Fetch CVE basic info and initial graph data
        const [cveDetails, securityGraph] = await Promise.all([
          puppyGraphService.getCVEDetails(cveId),
          puppyGraphService.getCVESecurityGraph(cveId)
        ]);

        if (cveDetails) {
          setCveInfo({
            id: cveDetails.id,
            score: cveDetails.score,
            severity: cveDetails.severity,
            description: cveDetails.description
          });
        }

        setGraphData(securityGraph);
      } catch (error) {
        console.error('Error fetching security graph data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, [cveId]);

  const handleViewChange = (event: React.MouseEvent<HTMLElement>, newView: GraphView | null) => {
    if (newView && newView !== currentView) {
      setCurrentView(newView);
      fetchGraphData(newView);
    }
  };

  const handleBackToCVE = () => {
    router.push('/cve');
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

  if (!cveId) {
    return (
      <DashboardLayout>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Security Graph
          </Typography>
          <Card>
            <CardContent>
              <Typography variant="body1" color="textSecondary">
                No CVE specified. Please navigate from a CVE details page or provide a CVE ID in the URL.
              </Typography>
              <Button 
                variant="contained" 
                onClick={handleBackToCVE}
                sx={{ mt: 2 }}
                startIcon={<ArrowBack />}
              >
                Go to CVE Analysis
              </Button>
            </CardContent>
          </Card>
        </Box>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box sx={{ 
          p: 2, 
          borderBottom: 1, 
          borderColor: 'divider',
          backgroundColor: 'background.paper',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          minHeight: 80
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<ArrowBack />}
              onClick={handleBackToCVE}
              sx={{ minWidth: 'auto' }}
            >
              Back to CVE Analysis
            </Button>
            <Box>
              <Typography variant="h5" component="h1" sx={{ fontWeight: 600 }}>
                Security Graph
              </Typography>
              {cveInfo && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                    {cveInfo.id}
                  </Typography>
                  <Chip 
                    label={cveInfo.severity} 
                    color={getSeverityColor(cveInfo.severity)}
                    size="small"
                    icon={<Security />}
                  />
                  <Chip 
                    label={`CVSS ${cveInfo.score}`} 
                    variant="outlined"
                    size="small"
                  />
                </Box>
              )}
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {graphData && (
              <Chip 
                label={`${graphData.nodes.length} nodes, ${graphData.links.length} connections`}
                variant="outlined"
                size="small"
                sx={{ fontFamily: 'monospace' }}
              />
            )}
          </Box>
        </Box>

        {/* View Selector */}
        <Box sx={{ 
          p: 2, 
          borderBottom: 1, 
          borderColor: 'divider',
          backgroundColor: 'background.default',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <ToggleButtonGroup
            value={currentView}
            exclusive
            onChange={handleViewChange}
            size="small"
            sx={{
              '& .MuiToggleButton-root': {
                px: 3,
                py: 1,
                textTransform: 'none',
                fontWeight: 500,
                border: 1,
                borderColor: 'divider',
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  }
                }
              }
            }}
          >
            <ToggleButton value="default">
              <AccountTree sx={{ mr: 1, fontSize: 18 }} />
              Default View
            </ToggleButton>
            <ToggleButton value="public-network">
              <Public sx={{ mr: 1, fontSize: 18 }} />
              Public Network Access
            </ToggleButton>
            <ToggleButton value="lateral-movement">
              <Hub sx={{ mr: 1, fontSize: 18 }} />
              Lateral Movement Risk
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Graph Container */}
        <Box sx={{ flex: 1, p: 2 }}>
          <Paper sx={{ 
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column',
            overflow: 'hidden',
            position: 'relative'
          }}>
            {viewLoading && (
              <Box sx={{ 
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                zIndex: 1000
              }}>
                <CircularProgress />
              </Box>
            )}
            
            {graphData && graphData.nodes.length > 0 ? (
              <Box sx={{ flex: 1, p: 1 }}>
                <SecurityGraph 
                  data={graphData}
                  height={window.innerHeight - 240} // Full height minus header, view selector and padding
                  resetKey={currentView}
                />
              </Box>
            ) : !viewLoading ? (
              <Box sx={{ 
                flex: 1, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                flexDirection: 'column',
                gap: 2
              }}>
                <Typography variant="h6" color="textSecondary">
                  {currentView === 'public-network' ? 
                    'No instances with public network access found' :
                   currentView === 'lateral-movement' ?
                    'No lateral movement risks found' :
                    'No security graph data available'
                  }
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {cveInfo ? 
                    (currentView === 'public-network' ? 
                      `No instances affected by ${cveInfo.id} have external network connections` :
                     currentView === 'lateral-movement' ?
                      `No internal instances affected by ${cveInfo.id} are connected to public instances` :
                      `No graph connections found for ${cveInfo.id}`) :
                    'Unable to load CVE information'
                  }
                </Typography>
              </Box>
            ) : null}
          </Paper>
        </Box>
      </Box>
    </DashboardLayout>
  );
}

export default function SecurityGraphPage() {
  return (
    <Suspense fallback={
      <DashboardLayout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      </DashboardLayout>
    }>
      <SecurityGraphContent />
    </Suspense>
  );
}