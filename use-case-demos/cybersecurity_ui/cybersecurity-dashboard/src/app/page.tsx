'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  Security as SecurityIcon,
  BugReport as BugReportIcon,
  Computer as ComputerIcon,
  NetworkCheck as NetworkIcon,
} from '@mui/icons-material';
import DashboardLayout from '@/components/Layout/DashboardLayout';
import { puppyGraphService } from '@/services/puppygraph';

const StatCard = ({ title, value, subtitle, icon, color, onClick }: {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  onClick?: () => void;
}) => (
  <Card 
    sx={{ 
      cursor: onClick ? 'pointer' : 'default',
      '&:hover': onClick ? { 
        boxShadow: 2,
        transform: 'translateY(-2px)',
        transition: 'all 0.2s ease-in-out'
      } : {}
    }}
    onClick={onClick}
  >
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography color="textSecondary" gutterBottom variant="body2">
            {title}
          </Typography>
          <Typography variant="h4" component="h2">
            {value}
          </Typography>
          <Typography color="textSecondary" variant="body2">
            {subtitle}
          </Typography>
        </Box>
        <Box sx={{ color }}>
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

export default function Dashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    criticalCves: 0,
    securityFindings: 0,
    ec2Instances: 0,
    networkFlows: 0
  });
  const [alerts, setAlerts] = useState<Array<{
    instance: string;
    cve: string;
    score: number;
    title: string;
  }>>([]);
  const [suspiciousTraffic, setSuspiciousTraffic] = useState<Array<{
    interfaceId: string;
    externalIp: string;
    port: number;
  }>>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashboardStats, recentAlerts, traffic] = await Promise.all([
          puppyGraphService.getDashboardStats(),
          puppyGraphService.getRecentAlerts(),
          puppyGraphService.getSuspiciousTraffic()
        ]);
        
        setStats(dashboardStats);
        setAlerts(recentAlerts);
        setSuspiciousTraffic(traffic);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
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
          Infrastructure Security Overview
        </Typography>
        
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Critical CVEs"
              value={stats.criticalCves.toLocaleString()}
              subtitle="Affecting infrastructure"
              icon={<BugReportIcon sx={{ fontSize: 40 }} />}
              color="#f44336"
              onClick={() => router.push('/cve')}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Security Findings"
              value={stats.securityFindings.toLocaleString()}
              subtitle="AWS Inspector alerts"
              icon={<SecurityIcon sx={{ fontSize: 40 }} />}
              color="#ff9800"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="EC2 Instances"
              value={stats.ec2Instances.toLocaleString()}
              subtitle="Monitored instances"
              icon={<ComputerIcon sx={{ fontSize: 40 }} />}
              color="#2196f3"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Network Flows"
              value={stats.networkFlows.toLocaleString()}
              subtitle="VPC flow logs analyzed"
              icon={<NetworkIcon sx={{ fontSize: 40 }} />}
              color="#4caf50"
            />
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 8 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Recent Security Alerts
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {alerts.slice(0, 4).map((alert, index) => (
                  <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">
                      {alert.cve} detected in {alert.instance}
                    </Typography>
                    <Chip 
                      label={alert.score >= 9 ? "Critical" : alert.score >= 7 ? "High" : "Medium"} 
                      color={alert.score >= 9 ? "error" : alert.score >= 7 ? "warning" : "info"} 
                      size="small" 
                    />
                  </Box>
                ))}
                {suspiciousTraffic.slice(0, 2).map((traffic, index) => (
                  <Box key={`traffic-${index}`} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">
                      Suspicious traffic to {traffic.externalIp}:{traffic.port}
                    </Typography>
                    <Chip label="High" color="warning" size="small" />
                  </Box>
                ))}
                {alerts.length === 0 && suspiciousTraffic.length === 0 && (
                  <Typography variant="body2" color="textSecondary">
                    No recent alerts found
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                  → Investigate CVE Impact
                </Typography>
                <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                  → Analyze Network Traffic
                </Typography>
                <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                  → Review Security Findings
                </Typography>
                <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                  → Generate Compliance Report
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </DashboardLayout>
  );
}