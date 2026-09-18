'use client';
import React from 'react';
import {
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import DashboardLayout from '@/components/Layout/DashboardLayout';

export default function SecurityFindings() {
  return (
    <DashboardLayout>
      <Box>
        <Typography variant="h4" component="h1" gutterBottom>
          Security Findings
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
          AWS Inspector security findings and recommendations
        </Typography>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Network Reachability
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Analyze network paths and reachability issues in your infrastructure
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Package Vulnerabilities
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Identify vulnerable packages and outdated software components
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </DashboardLayout>
  );
}