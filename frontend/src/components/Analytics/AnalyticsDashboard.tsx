import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Security,
  Warning,
  CheckCircle,
  Timeline,
} from '@mui/icons-material';

interface AnalyticsData {
  timeRange: string;
  totalScans: number;
  vulnerabilitiesFound: number;
  devicesScanned: number;
  riskTrend: 'up' | 'down' | 'stable';
  topVulnerabilities: Array<{
    name: string;
    count: number;
    severity: 'low' | 'medium' | 'high' | 'critical';
  }>;
  deviceTypes: Array<{
    type: string;
    count: number;
    riskScore: number;
  }>;
  scanHistory: Array<{
    date: string;
    scans: number;
    vulnerabilities: number;
  }>;
}

const AnalyticsDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      const mockData: AnalyticsData = {
        timeRange,
        totalScans: timeRange === '7d' ? 156 : timeRange === '30d' ? 642 : 1847,
        vulnerabilitiesFound: timeRange === '7d' ? 23 : timeRange === '30d' ? 89 : 267,
        devicesScanned: timeRange === '7d' ? 45 : timeRange === '30d' ? 78 : 124,
        riskTrend: Math.random() > 0.5 ? 'down' : 'up',
        topVulnerabilities: [
          { name: 'Weak Default Credentials', count: 12, severity: 'high' },
          { name: 'Unencrypted Communication', count: 8, severity: 'medium' },
          { name: 'Outdated Firmware', count: 15, severity: 'critical' },
          { name: 'Open Debug Ports', count: 6, severity: 'medium' },
          { name: 'Missing Authentication', count: 4, severity: 'critical' },
        ],
        deviceTypes: [
          { type: 'IP Cameras', count: 18, riskScore: 75 },
          { type: 'Smart Thermostats', count: 12, riskScore: 35 },
          { type: 'Smart Speakers', count: 8, riskScore: 45 },
          { type: 'Network Routers', count: 5, riskScore: 85 },
          { type: 'Smart TVs', count: 15, riskScore: 55 },
        ],
        scanHistory: [
          { date: '2025-01-15', scans: 23, vulnerabilities: 5 },
          { date: '2025-01-16', scans: 18, vulnerabilities: 3 },
          { date: '2025-01-17', scans: 31, vulnerabilities: 8 },
          { date: '2025-01-18', scans: 25, vulnerabilities: 4 },
          { date: '2025-01-19', scans: 29, vulnerabilities: 6 },
          { date: '2025-01-20', scans: 22, vulnerabilities: 2 },
          { date: '2025-01-21', scans: 27, vulnerabilities: 7 },
        ],
      };
      
      setAnalytics(mockData);
      setLoading(false);
    }, 1000);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'error';
    if (score >= 40) return 'warning';
    return 'success';
  };

  if (loading || !analytics) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Loading analytics...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Security Analytics
        </Typography>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            label="Time Range"
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <MenuItem value="7d">Last 7 days</MenuItem>
            <MenuItem value="30d">Last 30 days</MenuItem>
            <MenuItem value="90d">Last 90 days</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent sx={{ color: 'white' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {analytics.totalScans}
                  </Typography>
                  <Typography variant="body2">Total Scans</Typography>
                </Box>
                <Security sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <CardContent sx={{ color: 'white' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {analytics.vulnerabilitiesFound}
                  </Typography>
                  <Typography variant="body2">Vulnerabilities Found</Typography>
                </Box>
                <Warning sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <CardContent sx={{ color: 'white' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {analytics.devicesScanned}
                  </Typography>
                  <Typography variant="body2">Devices Scanned</Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
            <CardContent sx={{ color: 'white' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {analytics.riskTrend === 'down' ? '↓' : '↑'}
                  </Typography>
                  <Typography variant="body2">Risk Trend</Typography>
                </Box>
                {analytics.riskTrend === 'down' ? 
                  <TrendingDown sx={{ fontSize: 40, opacity: 0.8 }} /> :
                  <TrendingUp sx={{ fontSize: 40, opacity: 0.8 }} />
                }
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Top Vulnerabilities */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Vulnerabilities
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Vulnerability</TableCell>
                      <TableCell align="center">Count</TableCell>
                      <TableCell align="center">Severity</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {analytics.topVulnerabilities.map((vuln, index) => (
                      <TableRow key={index}>
                        <TableCell>{vuln.name}</TableCell>
                        <TableCell align="center">{vuln.count}</TableCell>
                        <TableCell align="center">
                          <Chip
                            label={vuln.severity.toUpperCase()}
                            color={getSeverityColor(vuln.severity)}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Device Types Risk Analysis */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Device Types Risk Analysis
              </Typography>
              <Box sx={{ mt: 2 }}>
                {analytics.deviceTypes.map((device, index) => (
                  <Box key={index} sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2">{device.type}</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          {device.count} devices
                        </Typography>
                        <Chip
                          label={`${device.riskScore}%`}
                          color={getRiskColor(device.riskScore)}
                          size="small"
                        />
                      </Box>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={device.riskScore}
                      color={getRiskColor(device.riskScore)}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Scan History Chart Placeholder */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Scan Activity Timeline
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 200, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Timeline sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Chart visualization would be implemented here
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    (Chart.js, D3.js, or similar charting library)
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsDashboard;