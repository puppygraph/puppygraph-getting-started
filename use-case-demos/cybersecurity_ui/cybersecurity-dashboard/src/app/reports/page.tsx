'use client';
import React from 'react';
import {
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import DashboardLayout from '@/components/Layout/DashboardLayout';

export default function Reports() {
  return (
    <DashboardLayout>
      <Box>
        <Typography variant="h4" component="h1" gutterBottom>
          Security Reports
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
          Generate and download security compliance and analysis reports
        </Typography>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <AssessmentIcon color="primary" />
                  <Typography variant="h6">
                    CVE Impact Report
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Comprehensive report on CVE impacts across your infrastructure
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  size="small"
                >
                  Generate Report
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <AssessmentIcon color="primary" />
                  <Typography variant="h6">
                    Compliance Summary
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Security compliance status and recommendations
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  size="small"
                >
                  Generate Report
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </DashboardLayout>
  );
}