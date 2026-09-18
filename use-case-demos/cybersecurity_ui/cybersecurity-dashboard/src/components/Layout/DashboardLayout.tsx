'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  AppBar,
  Avatar,
  Badge,
  Box,
  Breadcrumbs,
  Chip,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Toolbar,
  Typography,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  BugReport as BugReportIcon,
  NetworkCheck as NetworkIcon,
  Assessment as AssessmentIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Help as HelpIcon,
  Shield as ShieldIcon,
  AccountTree as SecurityGraphIcon,
} from '@mui/icons-material';

const drawerWidth = 280;

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const menuSections = [
  {
    title: 'Analytics & Intelligence',
    items: [
      { text: 'Executive Dashboard', icon: <DashboardIcon />, href: '/', badge: null },
      { text: 'Threat Intelligence', icon: <ShieldIcon />, href: '/findings', badge: null },
    ]
  },
  {
    title: 'Security Operations',
    items: [
      { text: 'Vulnerability Management', icon: <BugReportIcon />, href: '/cve', badge: '12' },
      { text: 'Security Graph', icon: <SecurityGraphIcon />, href: '/security-graph', badge: null },
      { text: 'Network Security', icon: <NetworkIcon />, href: '/network', badge: null },
      { text: 'Compliance Reports', icon: <AssessmentIcon />, href: '/reports', badge: null },
    ]
  }
];

const bottomMenuItems = [
  { text: 'Settings', icon: <SettingsIcon />, href: '/settings' },
  { text: 'Help & Support', icon: <HelpIcon />, href: '/help' },
];

const getBreadcrumbs = (pathname: string) => {
  const pathMap: { [key: string]: string } = {
    '/': 'Executive Dashboard',
    '/cve': 'Vulnerability Management',
    '/security-graph': 'Security Graph',
    '/findings': 'Threat Intelligence',
    '/network': 'Network Security',
    '/reports': 'Risk Analytics',
  };
  
  return pathMap[pathname] || 'Dashboard';
};

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();
  const theme = useTheme();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 3, borderBottom: `1px solid ${theme.palette.grey[700]}` }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
          <Image
            src="/puppy_logo.png"
            alt="PuppyGraph Logo"
            width={32}
            height={32}
            style={{ 
              borderRadius: '4px'
            }}
          />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1.125rem' }}>
              PuppyGraph Demo
            </Typography>
            <Typography variant="caption" sx={{ color: 'grey.400' }}>
              Cybersecurity Graph Intelligence
            </Typography>
          </Box>
        </Box>
      </Box>
      
      <Box sx={{ flexGrow: 1, overflowY: 'auto', py: 2 }}>
        {menuSections.map((section) => (
          <Box key={section.title} sx={{ mb: 3 }}>
            <ListSubheader
              sx={{
                bgcolor: 'transparent',
                color: 'grey.400',
                fontSize: '0.75rem',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                lineHeight: 1.5,
                px: 3,
                py: 1,
              }}
            >
              {section.title}
            </ListSubheader>
            <List dense sx={{ px: 1 }}>
              {section.items.map((item) => (
                <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                  <Link href={item.href} style={{ textDecoration: 'none', color: 'inherit', width: '100%' }}>
                    <ListItemButton 
                      selected={pathname === item.href}
                      sx={{ 
                        py: 1.5,
                        px: 2,
                        borderRadius: 1,
                        mx: 1,
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText 
                        primary={item.text}
                        primaryTypographyProps={{
                          fontSize: '0.875rem',
                          fontWeight: pathname === item.href ? 600 : 500,
                        }}
                      />
                      {item.badge && (
                        <Chip
                          label={item.badge}
                          size="small"
                          color={item.badge === 'New' ? 'success' : 'warning'}
                          sx={{ 
                            height: 20, 
                            fontSize: '0.625rem',
                            fontWeight: 600,
                          }}
                        />
                      )}
                    </ListItemButton>
                  </Link>
                </ListItem>
              ))}
            </List>
          </Box>
        ))}
      </Box>

      <Box sx={{ borderTop: `1px solid ${theme.palette.grey[700]}`, p: 1 }}>
        <List dense>
          {bottomMenuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <Link href={item.href} style={{ textDecoration: 'none', color: 'inherit', width: '100%' }}>
                <ListItemButton sx={{ py: 1, px: 2, borderRadius: 1 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.text}
                    primaryTypographyProps={{
                      fontSize: '0.875rem',
                      fontWeight: 500,
                    }}
                  />
                </ListItemButton>
              </Link>
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          zIndex: theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar sx={{ minHeight: '72px !important' }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
              {getBreadcrumbs(pathname)}
            </Typography>
            <Breadcrumbs 
              separator="/" 
              sx={{ 
                fontSize: '0.75rem',
                '& .MuiBreadcrumbs-separator': { 
                  color: 'grey.500',
                  mx: 0.5 
                }
              }}
            >
              <Typography variant="caption" sx={{ color: 'grey.400' }}>
                PuppyGraph Demo
              </Typography>
              <Typography variant="caption" sx={{ color: 'grey.300' }}>
                {getBreadcrumbs(pathname)}
              </Typography>
            </Breadcrumbs>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton 
              color="inherit" 
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.1)',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' }
              }}
            >
              <Badge badgeContent={3} color="error">
                <NotificationsIcon fontSize="small" />
              </Badge>
            </IconButton>
            <Box sx={{ ml: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ textAlign: 'right' }}>
                <Typography variant="body2" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                  Security Admin
                </Typography>
                <Typography variant="caption" sx={{ color: 'grey.300', lineHeight: 1 }}>
                  Enterprise User
                </Typography>
              </Box>
              <Avatar sx={{ bgcolor: 'secondary.main', width: 40, height: 40 }}>
                SA
              </Avatar>
            </Box>
          </Box>
        </Toolbar>
      </AppBar>
      
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          minHeight: '100vh',
          width: { md: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar sx={{ minHeight: '72px !important' }} />
        <Box sx={{ p: 4 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}