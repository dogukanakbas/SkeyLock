import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Avatar,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  Button,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Security,
  DevicesOther,
  Warning,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Refresh,
  Notifications,
  Router,
  Shield,
  BugReport,
  ViewModule,
  ViewList,
} from '@mui/icons-material';
import { useApi } from '../../contexts/ApiContext.tsx';

interface DashboardStats {
  totalDevices: number;
  activeDevices: number;
  vulnerabilities: number;
  criticalVulns: number;
  riskScore: number;
  lastScan: string;
}

interface RecentActivity {
  id: number;
  type: 'scan' | 'vulnerability' | 'device';
  message: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

const ModernDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalDevices: 0,
    activeDevices: 0,
    vulnerabilities: 0,
    criticalVulns: 0,
    riskScore: 0,
    lastScan: '',
  });
  
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [compactView, setCompactView] = useState(false);
  const { getDevices, getScans } = useApi();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch devices
      const devices = await getDevices();
      const scans = await getScans();
      
      // Calculate stats
      const totalDevices = devices.length;
      const activeDevices = devices.filter(d => d.is_active).length;
      const vulnerabilities = devices.reduce((sum, d) => sum + d.vulnerabilities_count, 0);
      const criticalVulns = devices.reduce((sum, d) => sum + d.critical_vulnerabilities, 0);
      const avgRiskScore = devices.length > 0 
        ? devices.reduce((sum, d) => sum + d.risk_score, 0) / devices.length 
        : 0;
      
      setStats({
        totalDevices,
        activeDevices,
        vulnerabilities,
        criticalVulns,
        riskScore: Math.round(avgRiskScore),
        lastScan: scans.length > 0 ? scans[0].started_at : '',
      });

      // Generate recent activity
      const activities: RecentActivity[] = [
        {
          id: 1,
          type: 'scan',
          message: 'Security scan completed on 192.168.1.100',
          timestamp: '2 minutes ago',
          severity: 'low',
        },
        {
          id: 2,
          type: 'vulnerability',
          message: 'Critical vulnerability detected on smart camera',
          timestamp: '15 minutes ago',
          severity: 'critical',
        },
        {
          id: 3,
          type: 'device',
          message: 'New IoT device discovered: Smart Thermostat',
          timestamp: '1 hour ago',
          severity: 'low',
        },
        {
          id: 4,
          type: 'vulnerability',
          message: 'Medium risk vulnerability patched',
          timestamp: '2 hours ago',
          severity: 'medium',
        },
      ];
      
      setRecentActivity(activities);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'error';
    if (score >= 40) return 'warning';
    return 'success';
  };

  const getRiskLabel = (score: number) => {
    if (score >= 70) return 'High Risk';
    if (score >= 40) return 'Medium Risk';
    return 'Low Risk';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#f44336';
      case 'high': return '#ff9800';
      case 'medium': return '#ffeb3b';
      case 'low': return '#4caf50';
      default: return '#9e9e9e';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'scan': return <Security />;
      case 'vulnerability': return <BugReport />;
      case 'device': return <Router />;
      default: return <Notifications />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Loading dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Security Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch
                checked={compactView}
                onChange={(e) => setCompactView(e.target.checked)}
                color="primary"
                size="small"
              />
            }
            label="Compact"
            sx={{ mr: 2 }}
          />
          <IconButton onClick={fetchDashboardData} color="primary" title="Refresh Data">
            <Refresh />
          </IconButton>
          <Button variant="outlined" startIcon={<Security />}>
            Run Full Scan
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent sx={{ color: 'white' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {stats.totalDevices}
                  </Typography>
                  <Typography variant="body2">
                    Total Devices
                  </Typography>
                </Box>
                <DevicesOther sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <CardContent sx={{ color: 'white' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {stats.activeDevices}
                  </Typography>
                  <Typography variant="body2">
                    Active Devices
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <CardContent sx={{ color: 'white' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {stats.vulnerabilities}
                  </Typography>
                  <Typography variant="body2">
                    Vulnerabilities
                  </Typography>
                </Box>
                <Warning sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
            <CardContent sx={{ color: 'white' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {stats.criticalVulns}
                  </Typography>
                  <Typography variant="body2">
                    Critical Issues
                  </Typography>
                </Box>
                <Shield sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Risk Score */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Overall Risk Score
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h3" component="div" fontWeight="bold" sx={{ mr: 2 }}>
                  {stats.riskScore}
                </Typography>
                <Chip 
                  label={getRiskLabel(stats.riskScore)}
                  color={getRiskColor(stats.riskScore)}
                  size="small"
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={stats.riskScore} 
                color={getRiskColor(stats.riskScore)}
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Based on {stats.totalDevices} devices analyzed
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List>
                {recentActivity.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: getSeverityColor(activity.severity) }}>
                          {getActivityIcon(activity.type)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={activity.message}
                        secondary={activity.timestamp}
                      />
                    </ListItem>
                    {index < recentActivity.length - 1 && <Divider variant="inset" component="li" />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button variant="contained" startIcon={<Security />}>
                Start Security Scan
              </Button>
              <Button variant="outlined" startIcon={<DevicesOther />}>
                Add New Device
              </Button>
              <Button variant="outlined" startIcon={<TrendingUp />}>
                View Reports
              </Button>
              <Button variant="outlined" startIcon={<Notifications />}>
                Configure Alerts
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ModernDashboard;