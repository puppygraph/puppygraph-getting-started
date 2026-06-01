'use client';
import React from 'react';
import {
  Drawer,
  Typography,
  Box,
  IconButton,
  Divider,
  Chip,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Tabs,
  Tab,
  Button,
} from '@mui/material';
import { Close as CloseIcon, Security, Computer, NetworkCheck, Warning, Fullscreen, FullscreenExit, Link as LinkIcon, AccountTree as SecurityGraphIcon, OpenInNew } from '@mui/icons-material';
import SecurityGraph from './SecurityGraph';

interface CVEDetail {
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
}

interface CVEDetailsSectionLoading {
  affectedInstances: boolean;
  networkConnections: boolean;
  relatedFindings: boolean;
  securityGraph: boolean;
}

interface CVEDetailsPanelProps {
  open: boolean;
  onClose: () => void;
  cveDetails: CVEDetail | null;
  loading: boolean;
  sectionLoading?: CVEDetailsSectionLoading;
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

export default function CVEDetailsPanel({ open, onClose, cveDetails, loading, sectionLoading }: CVEDetailsPanelProps) {
  const [isFullscreen, setIsFullscreen] = React.useState(false);
  const [tabValue, setTabValue] = React.useState(0);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const openInSecurityGraph = () => {
    if (cveDetails) {
      const url = `/security-graph?cve=${encodeURIComponent(cveDetails.id)}`;
      window.open(url, '_blank');
    }
  };
  if (loading) {
    return (
      <Drawer 
        anchor="right" 
        open={open} 
        onClose={onClose}
        PaperProps={{
          sx: {
            width: isFullscreen ? '100vw' : '900px',
            maxWidth: '100vw',
            zIndex: (theme) => theme.zIndex.modal + 1
          }
        }}
        ModalProps={{
          sx: {
            zIndex: (theme) => theme.zIndex.modal + 1
          }
        }}
      >
        <Box sx={{ width: '100%', p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <CircularProgress />
        </Box>
      </Drawer>
    );
  }

  if (!cveDetails) {
    return (
      <Drawer 
        anchor="right" 
        open={open} 
        onClose={onClose}
        PaperProps={{
          sx: {
            width: isFullscreen ? '100vw' : '900px',
            maxWidth: '100vw'
          }
        }}
      >
        <Box sx={{ width: '100%', p: 3 }}>
          <Typography>No CVE details available</Typography>
        </Box>
      </Drawer>
    );
  }

  return (
    <Drawer 
      anchor="right" 
      open={open} 
      onClose={onClose}
      PaperProps={{
        sx: {
          width: isFullscreen ? '100vw' : '900px',
          maxWidth: '100vw',
          zIndex: (theme) => theme.zIndex.modal + 1
        }
      }}
      ModalProps={{
        sx: {
          zIndex: (theme) => theme.zIndex.modal + 1
        }
      }}
    >
      <Box sx={{ width: '100%', height: '100%', overflow: 'auto' }}>
        <Box sx={{ 
          p: 2, 
          borderBottom: 1, 
          borderColor: 'divider', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          backgroundColor: 'background.paper',
          minHeight: 64
        }}>
          <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
            CVE Details
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <IconButton 
              onClick={toggleFullscreen} 
              title={isFullscreen ? "Exit fullscreen" : "Expand to fullscreen"}
              sx={{ 
                bgcolor: 'action.hover',
                border: 1,
                borderColor: 'divider',
                '&:hover': { 
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  borderColor: 'primary.main'
                }
              }}
            >
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
            <IconButton 
              onClick={onClose}
              sx={{ 
                '&:hover': { 
                  bgcolor: 'error.main',
                  color: 'error.contrastText'
                }
              }}
            >
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>

        <Box sx={{ p: 3 }}>
          {/* CVE Header */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h5" sx={{ fontFamily: 'monospace', mb: 1 }}>
              {cveDetails.id}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip 
                label={cveDetails.severity} 
                color={getSeverityColor(cveDetails.severity)}
                icon={<Security />}
              />
              <Chip 
                label={`CVSS ${cveDetails.score}`} 
                variant="outlined"
              />
            </Box>
            <Typography variant="body1" sx={{ mb: 2 }}>
              {cveDetails.description}
            </Typography>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {/* CVE Metadata */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Security sx={{ verticalAlign: 'middle', mr: 1 }} />
                Vulnerability Details
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="body2" color="textSecondary">Published</Typography>
                  <Typography variant="body1">{cveDetails.publishedDate}</Typography>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="body2" color="textSecondary">Last Modified</Typography>
                  <Typography variant="body1">{cveDetails.lastModified}</Typography>
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="body2" color="textSecondary">Vector String</Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', backgroundColor: 'grey.200', color: 'grey.800', p: 1, borderRadius: 1 }}>
                    {cveDetails.vectorString}
                  </Typography>
                </Grid>
                {cveDetails.weaknesses.length > 0 && (
                  <Grid size={{ xs: 12 }}>
                    <Typography variant="body2" color="textSecondary">Weaknesses</Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                      {cveDetails.weaknesses.map((weakness, index) => (
                        <Chip key={index} label={weakness} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>

          {/* Two Column Layout for Affected Instances and Network Connections */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Computer sx={{ verticalAlign: 'middle' }} />
                    Affected Instances
                    <Chip 
                      label={cveDetails.affectedInstances?.length || 0} 
                      size="small" 
                      color="primary"
                    />
                  </Typography>
                  {sectionLoading?.affectedInstances ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                      <CircularProgress />
                    </Box>
                  ) : (
                    <TableContainer 
                      sx={{
                        maxHeight: '300px',
                        overflow: 'auto',
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1
                      }}
                    >
                      <Table size="small" stickyHeader>
                        <TableHead>
                          <TableRow>
                            <TableCell>Instance ID</TableCell>
                            <TableCell>Finding</TableCell>
                            <TableCell>Subnet</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {cveDetails.affectedInstances?.map((instance, index) => (
                            <TableRow key={index} hover>
                              <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.813rem' }}>{instance.instanceId}</TableCell>
                              <TableCell sx={{ fontSize: '0.813rem' }}>{instance.findingTitle}</TableCell>
                              <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.813rem' }}>{instance.subnetId}</TableCell>
                            </TableRow>
                          )) || (
                            <TableRow>
                              <TableCell colSpan={3} align="center" sx={{ py: 4, color: 'text.secondary', fontStyle: 'italic' }}>
                                No affected instances found
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </CardContent>
              </Card>
            </Grid>
            
            <Grid size={{ xs: 12, md: 6 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <NetworkCheck sx={{ verticalAlign: 'middle' }} />
                    Network Connections
                    <Chip 
                      label={cveDetails.networkConnections?.length || 0} 
                      size="small" 
                      color="primary"
                    />
                  </Typography>
                  {sectionLoading?.networkConnections ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                      <CircularProgress />
                    </Box>
                  ) : (
                    <TableContainer 
                      sx={{
                        maxHeight: '300px',
                        overflow: 'auto',
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1
                      }}
                    >
                      <Table size="small" stickyHeader>
                        <TableHead>
                          <TableRow>
                            <TableCell>Interface</TableCell>
                            <TableCell>External IP</TableCell>
                            <TableCell>Port</TableCell>
                            <TableCell>Status</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {cveDetails.networkConnections && cveDetails.networkConnections.length > 0 ? (
                            cveDetails.networkConnections.map((conn, index) => (
                              <TableRow key={index} hover>
                                <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.813rem' }}>{conn.interfaceId}</TableCell>
                                <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.813rem' }}>{conn.externalIp}</TableCell>
                                <TableCell sx={{ fontSize: '0.813rem' }}>{conn.port}</TableCell>
                                <TableCell>
                                  <Chip 
                                    label={conn.isMalicious ? "Malicious" : "Clean"} 
                                    color={conn.isMalicious ? "error" : "success"}
                                    size="small"
                                    sx={{ fontWeight: 500 }}
                                  />
                                </TableCell>
                              </TableRow>
                            ))
                          ) : (
                            <TableRow>
                              <TableCell colSpan={4} align="center" sx={{ py: 4, color: 'text.secondary', fontStyle: 'italic' }}>
                                No network connections found
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Security Graph Section */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SecurityGraphIcon sx={{ verticalAlign: 'middle' }} />
                  Security Graph
                  <Chip 
                    label={cveDetails.securityGraph?.nodes?.length || 0} 
                    size="small" 
                    color="primary"
                  />
                </Typography>
                {cveDetails.securityGraph && cveDetails.securityGraph.nodes.length > 0 && (
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<OpenInNew />}
                    onClick={openInSecurityGraph}
                    sx={{ 
                      minWidth: 'auto',
                      textTransform: 'none',
                      borderColor: 'primary.main',
                      color: 'primary.main',
                      '&:hover': {
                        backgroundColor: 'primary.main',
                        color: 'primary.contrastText',
                        borderColor: 'primary.main'
                      }
                    }}
                  >
                    Open in Security Graph
                  </Button>
                )}
              </Box>
              {sectionLoading?.securityGraph ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : cveDetails.securityGraph ? (
                <Box sx={{ width: '100%' }}>
                  <SecurityGraph 
                    data={cveDetails.securityGraph}
                    height={500}
                    showInfoPanel={false}
                  />
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ p: 4, textAlign: 'center', fontStyle: 'italic' }}>
                  No security graph data available
                </Typography>
              )}
            </CardContent>
          </Card>

          {/* Tabs for Related Findings and References */}
          <Box sx={{ 
            borderBottom: 2, 
            borderColor: 'divider',
            backgroundColor: (theme) => theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50',
            borderRadius: '8px 8px 0 0',
            overflow: 'hidden'
          }}>
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange} 
              aria-label="CVE details tabs"
              variant="fullWidth"
              sx={{
                minHeight: 48,
                '& .MuiTabs-indicator': {
                  height: 3,
                  backgroundColor: 'primary.main',
                  borderRadius: '3px 3px 0 0'
                },
                '& .MuiTab-root': {
                  minHeight: 48,
                  textTransform: 'none',
                  fontWeight: 500,
                  fontSize: '0.875rem',
                  color: 'text.secondary',
                  borderRight: '1px solid',
                  borderColor: 'divider',
                  '&:last-child': {
                    borderRight: 'none'
                  },
                  '&.Mui-selected': {
                    color: 'primary.main',
                    backgroundColor: 'background.paper',
                    fontWeight: 600
                  },
                  '&:hover': {
                    backgroundColor: 'action.hover',
                    color: 'text.primary'
                  }
                }
              }}
            >
              <Tab 
                label={
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5, py: 0.5 }}>
                    <Warning fontSize="small" />
                    <Typography variant="body2" sx={{ fontWeight: 'inherit', lineHeight: 1.2 }}>
                      Related Findings
                    </Typography>
                    <Chip 
                      label={cveDetails.relatedFindings?.length || 0} 
                      size="small" 
                      variant="outlined"
                      sx={{ 
                        height: 18, 
                        fontSize: '0.7rem',
                        backgroundColor: tabValue === 0 ? 'primary.main' : (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100',
                        color: tabValue === 0 ? 'primary.contrastText' : 'text.secondary',
                        borderColor: tabValue === 0 ? 'primary.main' : 'divider'
                      }}
                    />
                  </Box>
                } 
              />
              <Tab 
                label={
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5, py: 0.5 }}>
                    <LinkIcon fontSize="small" />
                    <Typography variant="body2" sx={{ fontWeight: 'inherit', lineHeight: 1.2 }}>
                      References
                    </Typography>
                    <Chip 
                      label={cveDetails.references?.length || 0} 
                      size="small" 
                      variant="outlined"
                      sx={{ 
                        height: 18, 
                        fontSize: '0.7rem',
                        backgroundColor: tabValue === 1 ? 'primary.main' : (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100',
                        color: tabValue === 1 ? 'primary.contrastText' : 'text.secondary',
                        borderColor: tabValue === 1 ? 'primary.main' : 'divider'
                      }}
                    />
                  </Box>
                } 
              />
            </Tabs>
          </Box>

          {/* Tab Panels */}
          <Box sx={{ 
            backgroundColor: 'background.paper',
            border: 1,
            borderColor: 'divider',
            borderTop: 'none',
            borderRadius: '0 0 8px 8px',
            maxHeight: '60vh',
            overflow: 'hidden'
          }}>
            {/* Related Findings Tab */}
            {tabValue === 0 && (
              <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                {sectionLoading?.relatedFindings ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <Box sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    backgroundColor: 'background.paper',
                    maxHeight: '50vh',
                    overflow: 'auto'
                  }}>
                    {cveDetails.relatedFindings && cveDetails.relatedFindings.length > 0 ? (
                      <List dense sx={{ p: 0 }}>
                        {cveDetails.relatedFindings.map((finding, index) => (
                          <ListItem 
                            key={index} 
                            divider={index < cveDetails.relatedFindings!.length - 1}
                            sx={{
                              py: 2,
                              px: 2,
                              '&:hover': {
                                backgroundColor: 'action.hover'
                              },
                              borderBottom: index < cveDetails.relatedFindings!.length - 1 ? 1 : 0,
                              borderColor: 'divider'
                            }}
                          >
                            <ListItemText
                              primary={
                                <Typography variant="body2" sx={{ fontWeight: 500, mb: 1 }}>
                                  {finding.title}
                                </Typography>
                              }
                              secondary={
                                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                                  <Chip 
                                    label={finding.severity} 
                                    size="small" 
                                    color={getSeverityColor(finding.severity)}
                                    sx={{ fontWeight: 500 }}
                                  />
                                  {finding.packageName && (
                                    <Chip 
                                      label={finding.packageName} 
                                      size="small" 
                                      variant="outlined"
                                      sx={{ 
                                        backgroundColor: (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.50',
                                        borderColor: 'divider'
                                      }}
                                    />
                                  )}
                                </Box>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary" sx={{ p: 4, textAlign: 'center', fontStyle: 'italic' }}>
                        No related findings found
                      </Typography>
                    )}
                  </Box>
                )}
              </Box>
            )}

            {/* References Tab */}
            {tabValue === 1 && (
              <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                <Box sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  backgroundColor: 'background.paper',
                  maxHeight: '50vh',
                  overflow: 'auto'
                }}>
                  {cveDetails.references && cveDetails.references.length > 0 ? (
                    <List dense sx={{ p: 0 }}>
                      {cveDetails.references.map((ref, index) => (
                        <ListItem 
                          key={index}
                          sx={{
                            py: 2,
                            px: 2,
                            '&:hover': {
                              backgroundColor: 'action.hover'
                            },
                            borderBottom: index < cveDetails.references!.length - 1 ? 1 : 0,
                            borderColor: 'divider'
                          }}
                        >
                          <ListItemText
                            primary={
                              <Typography 
                                component="a" 
                                href={ref} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                variant="body2"
                                sx={{ 
                                  color: 'primary.main', 
                                  textDecoration: 'none', 
                                  fontWeight: 500,
                                  '&:hover': { 
                                    textDecoration: 'underline',
                                    color: 'primary.dark'
                                  }
                                }}
                              >
                                {ref}
                              </Typography>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary" sx={{ p: 4, textAlign: 'center', fontStyle: 'italic' }}>
                      No references available
                    </Typography>
                  )}
                </Box>
              </Box>
            )}
          </Box>
        </Box>
      </Box>
    </Drawer>
  );
}