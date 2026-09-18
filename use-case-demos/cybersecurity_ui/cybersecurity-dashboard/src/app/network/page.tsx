'use client';
import React, { useEffect, useState } from 'react';
import {
  Typography,
  Box,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
} from '@mui/material';
import DashboardLayout from '@/components/Layout/DashboardLayout';
import { puppyGraphService } from '@/services/puppygraph';

export default function NetworkAnalysis() {
  const [loading, setLoading] = useState(true);
  const [networkData, setNetworkData] = useState<{
    topExternalConnections?: Array<{ Values: [string, boolean, number]; Keys: string[] }>;
    suspiciousInstances?: Array<{ Values: [string, number]; Keys: string[] }>;
    topPorts?: Array<{ Values: [number, number]; Keys: string[] }>;
  }>({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await puppyGraphService.getNetworkAnalysisData();
        setNetworkData(data);
      } catch (error) {
        console.error('Error fetching network data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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
          Network Analysis
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
          VPC flow logs analysis and network security monitoring
        </Typography>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Top External Connections
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>IP Address</TableCell>
                      <TableCell>Connections</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {networkData.topExternalConnections?.map((conn, index: number) => (
                      <TableRow key={index}>
                        <TableCell sx={{ fontFamily: 'monospace' }}>
                          {conn.Values[0]}
                        </TableCell>
                        <TableCell>{conn.Values[2]}</TableCell>
                        <TableCell>
                          <Chip 
                            label={conn.Values[1] ? "Malicious" : "Clean"} 
                            color={conn.Values[1] ? "error" : "success"}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    )) || []}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
          
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Instances with Suspicious Activity
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Instance ID</TableCell>
                      <TableCell>Malicious Connections</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {networkData.suspiciousInstances?.map((instance, index: number) => (
                      <TableRow key={index}>
                        <TableCell sx={{ fontFamily: 'monospace' }}>
                          {instance.Values[0]}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={instance.Values[1]} 
                            color="error" 
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    )) || []}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
          
          <Grid size={{ xs: 12 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Most Used Ports
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Port</TableCell>
                      <TableCell>Usage Count</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {networkData.topPorts?.map((port, index: number) => (
                      <TableRow key={index}>
                        <TableCell sx={{ fontFamily: 'monospace' }}>
                          {port.Values[0]}
                        </TableCell>
                        <TableCell>{port.Values[1]}</TableCell>
                      </TableRow>
                    )) || []}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </DashboardLayout>
  );
}