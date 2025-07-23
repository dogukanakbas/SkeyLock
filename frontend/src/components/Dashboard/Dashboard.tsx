import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Button,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Devices,
  Security,
  Warning,
  TrendingUp
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext.tsx';
import { useApi } from '../../contexts/ApiContext.tsx';
import { useNavigate } from 'react-router-dom';
import ModernDashboard from './ModernDashboard.tsx';

interface Stats {
  total_devices: number;
  active_devices: number;
  total_scans: number;
  recent_scans: number;
  critical_vulnerabilities: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [modernView, setModernView] = useState(true);
  const { user } = useAuth();
  const { getDevices, getScans } = useApi();
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      // Fetch devices and scans to calculate stats
      const [devices, scans] = await Promise.all([
        getDevices(),
        getScans()
      ]);

      const stats: Stats = {
        total_devices: devices.length,
        active_devices: devices.filter(d => d.is_active).length,
        total_scans: scans.length,
        recent_scans: scans.filter(s => s.status === 'completed').length,
        critical_vulnerabilities: devices.reduce((sum, d) => sum + d.critical_vulnerabilities, 0)
      };

      setStats(stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
    color: string;
    onClick?: () => void;
  }> = ({ title, value, icon, color, onClick }) => (
    <Card 
      sx={{ cursor: onClick ? 'pointer' : 'default' }}
      onClick={onClick}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color, fontSize: 40 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return <LinearProgress />;
  }

  // Modern view'i göster
  if (modernView) {
    return <ModernDashboard />;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <FormControlLabel
          control={
            <Switch
              checked={modernView}
              onChange={(e) => setModernView(e.target.checked)}
              color="primary"
            />
          }
          label="Modern View"
        />
      </Box>
      
      {/* Trial Warning */}
      {user?.subscription_plan === 'demo' && (
        <Alert 
          severity="warning" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={() => navigate('/subscription')}>
              Upgrade Now
            </Button>
          }
        >
          Your trial expires in {user.trial_days_left} days. Upgrade to continue using all features.
        </Alert>
      )}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Devices"
            value={stats?.total_devices || 0}
            icon={<Devices />}
            color="#1976d2"
            onClick={() => navigate('/devices')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Devices"
            value={stats?.active_devices || 0}
            icon={<TrendingUp />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Scans"
            value={stats?.total_scans || 0}
            icon={<Security />}
            color="#ed6c02"
            onClick={() => navigate('/scans')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Critical Issues"
            value={stats?.critical_vulnerabilities || 0}
            icon={<Warning />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Button 
                variant="contained" 
                startIcon={<Devices />}
                onClick={() => navigate('/devices')}
              >
                Add New Device
              </Button>
              <Button 
                variant="outlined" 
                startIcon={<Security />}
                onClick={() => navigate('/scans')}
              >
                Start Security Scan
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Subscription Status
            </Typography>
            <Typography variant="body1" gutterBottom>
              Plan: <strong>{user?.subscription_plan?.toUpperCase()}</strong>
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Status: {user?.subscription_status}
            </Typography>
            {user?.subscription_plan === 'demo' && (
              <Button 
                variant="contained" 
                color="primary" 
                sx={{ mt: 2 }}
                onClick={() => navigate('/subscription')}
              >
                Upgrade Plan
              </Button>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;