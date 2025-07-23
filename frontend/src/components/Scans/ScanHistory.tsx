import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  LinearProgress,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Collapse
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Visibility,
  ExpandMore,
  ExpandLess,
  Security,
  NetworkCheck,
  BugReport
} from '@mui/icons-material';
import { useApi } from '../../contexts/ApiContext.tsx';

interface Scan {
  id: number;
  device_id: number;
  device_name: string;
  device_ip: string;
  scan_type: string;
  status: string;
  started_at: string;
  completed_at?: string;
  results?: any;
  error_message?: string;
  duration?: number;
}

const ScanHistory: React.FC = () => {
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedScan, setSelectedScan] = useState<Scan | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const { getScans, createScan } = useApi();

  useEffect(() => {
    fetchScans();
  }, []);

  const fetchScans = async () => {
    try {
      const scanData = await getScans();
      setScans(scanData);
    } catch (error) {
      console.error('Failed to fetch scans:', error);
      // Mock data for demo
      setScans([
        {
          id: 1,
          device_id: 1,
          device_name: 'Smart Camera 01',
          device_ip: '192.168.1.100',
          scan_type: 'full',
          status: 'completed',
          started_at: '2024-01-21T10:00:00Z',
          completed_at: '2024-01-21T10:05:30Z',
          duration: 330,
          results: {
            open_ports: [80, 443, 554],
            vulnerabilities: ['CVE-2023-1234', 'CVE-2023-5678'],
            risk_score: 75.5
          }
        },
        {
          id: 2,
          device_id: 2,
          device_name: 'Smart Thermostat',
          device_ip: '192.168.1.101',
          scan_type: 'quick',
          status: 'completed',
          started_at: '2024-01-21T09:30:00Z',
          completed_at: '2024-01-21T09:32:15Z',
          duration: 135,
          results: {
            open_ports: [80],
            vulnerabilities: [],
            risk_score: 25.0
          }
        },
        {
          id: 3,
          device_id: 1,
          device_name: 'Smart Camera 01',
          device_ip: '192.168.1.100',
          scan_type: 'vulnerability',
          status: 'running',
          started_at: '2024-01-21T14:00:00Z'
        },
        {
          id: 4,
          device_id: 3,
          device_name: 'Smart Doorbell',
          device_ip: '192.168.1.102',
          scan_type: 'port',
          status: 'failed',
          started_at: '2024-01-21T13:00:00Z',
          completed_at: '2024-01-21T13:01:00Z',
          error_message: 'Device unreachable'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusChip = (status: string) => {
    const statusConfig: { [key: string]: { color: 'success' | 'warning' | 'error' | 'info', label: string } } = {
      completed: { color: 'success', label: 'Completed' },
      running: { color: 'warning', label: 'Running' },
      failed: { color: 'error', label: 'Failed' },
      pending: { color: 'info', label: 'Pending' }
    };
    const config = statusConfig[status] || { color: 'info', label: status };
    return <Chip label={config.label} color={config.color} size="small" />;
  };

  const getScanTypeChip = (type: string) => {
    const typeConfig: { [key: string]: { color: 'primary' | 'secondary' | 'default', icon: React.ReactElement } } = {
      full: { color: 'primary', icon: <Security /> },
      quick: { color: 'default', icon: <NetworkCheck /> },
      port: { color: 'secondary', icon: <NetworkCheck /> },
      vulnerability: { color: 'primary', icon: <BugReport /> }
    };
    const config = typeConfig[type] || { color: 'default', icon: <Security /> };
    return <Chip label={type.toUpperCase()} color={config.color} size="small" icon={config.icon} />;
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const toggleRowExpansion = (scanId: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(scanId)) {
      newExpanded.delete(scanId);
    } else {
      newExpanded.add(scanId);
    }
    setExpandedRows(newExpanded);
  };

  const handleViewDetails = (scan: Scan) => {
    setSelectedScan(scan);
    setDetailsOpen(true);
  };

  const handleNewScan = async () => {
    try {
      // For demo, scan the first available device
      const firstDeviceId = 1; // You could make this dynamic
      console.log('Starting new scan...');

      const scanResult = await createScan({
        device_id: firstDeviceId,
        scan_type: 'quick'
      });

      console.log('New scan started:', scanResult);
      alert(`New scan started successfully! Scan ID: ${scanResult.id}`);

      // Refresh scans list
      setTimeout(() => {
        fetchScans();
      }, 1000);

    } catch (error) {
      console.error('Failed to start new scan:', error);
      alert('Failed to start scan. Please try again.');
    }
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Security Scans ({scans.length})
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchScans}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={handleNewScan}
          >
            New Scan
          </Button>
        </Box>
      </Box>

      {/* Scan Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Completed Scans
              </Typography>
              <Typography variant="h4" color="success.main">
                {scans.filter(s => s.status === 'completed').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Running Scans
              </Typography>
              <Typography variant="h4" color="warning.main">
                {scans.filter(s => s.status === 'running').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Failed Scans
              </Typography>
              <Typography variant="h4" color="error.main">
                {scans.filter(s => s.status === 'failed').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Vulnerabilities Found
              </Typography>
              <Typography variant="h4" color="error.main">
                {scans.reduce((sum, s) => sum + (s.results?.vulnerabilities?.length || 0), 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Scans Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell width="50px"></TableCell>
                  <TableCell>Device</TableCell>
                  <TableCell>Scan Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Started</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Results</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {scans.map((scan) => (
                  <React.Fragment key={scan.id}>
                    <TableRow>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => toggleRowExpansion(scan.id)}
                        >
                          {expandedRows.has(scan.id) ? <ExpandLess /> : <ExpandMore />}
                        </IconButton>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="subtitle2">
                            {scan.device_name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {scan.device_ip}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{getScanTypeChip(scan.scan_type)}</TableCell>
                      <TableCell>{getStatusChip(scan.status)}</TableCell>
                      <TableCell>
                        {new Date(scan.started_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        {scan.duration ? formatDuration(scan.duration) :
                          scan.status === 'running' ? 'Running...' : '-'}
                      </TableCell>
                      <TableCell>
                        {scan.results ? (
                          <Box>
                            <Typography variant="body2">
                              {scan.results.open_ports?.length || 0} ports
                            </Typography>
                            <Typography variant="body2" color="error">
                              {scan.results.vulnerabilities?.length || 0} vulnerabilities
                            </Typography>
                          </Box>
                        ) : scan.error_message ? (
                          <Typography variant="body2" color="error">
                            Error
                          </Typography>
                        ) : '-'}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<Visibility />}
                          onClick={() => handleViewDetails(scan)}
                          disabled={!scan.results && !scan.error_message}
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={8}>
                        <Collapse in={expandedRows.has(scan.id)} timeout="auto" unmountOnExit>
                          <Box sx={{ margin: 1 }}>
                            {scan.results && (
                              <Box>
                                <Typography variant="h6" gutterBottom>
                                  Scan Results
                                </Typography>
                                <Grid container spacing={2}>
                                  <Grid item xs={4}>
                                    <Typography variant="subtitle2">Open Ports:</Typography>
                                    <Typography variant="body2">
                                      {scan.results.open_ports?.join(', ') || 'None'}
                                    </Typography>
                                  </Grid>
                                  <Grid item xs={4}>
                                    <Typography variant="subtitle2">Vulnerabilities:</Typography>
                                    <Typography variant="body2">
                                      {scan.results.vulnerabilities?.join(', ') || 'None'}
                                    </Typography>
                                  </Grid>
                                  <Grid item xs={4}>
                                    <Typography variant="subtitle2">Risk Score:</Typography>
                                    <Typography variant="body2" color={scan.results.risk_score > 70 ? 'error' : scan.results.risk_score > 40 ? 'warning.main' : 'success.main'}>
                                      {scan.results.risk_score}/100
                                    </Typography>
                                  </Grid>
                                </Grid>
                              </Box>
                            )}
                            {scan.error_message && (
                              <Box>
                                <Typography variant="h6" gutterBottom color="error">
                                  Error Details
                                </Typography>
                                <Typography variant="body2" color="error">
                                  {scan.error_message}
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        </Collapse>
                      </TableCell>
                    </TableRow>
                  </React.Fragment>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Scan Details Dialog */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Scan Details - {selectedScan?.device_name}
        </DialogTitle>
        <DialogContent>
          {selectedScan && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Scan Type:</Typography>
                  <Typography variant="body2">{selectedScan.scan_type}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Status:</Typography>
                  <Typography variant="body2">{selectedScan.status}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Started:</Typography>
                  <Typography variant="body2">
                    {new Date(selectedScan.started_at).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Duration:</Typography>
                  <Typography variant="body2">
                    {selectedScan.duration ? formatDuration(selectedScan.duration) : 'N/A'}
                  </Typography>
                </Grid>
              </Grid>

              {selectedScan.results && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom>Results</Typography>
                  <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '4px', overflow: 'auto' }}>
                    {JSON.stringify(selectedScan.results, null, 2)}
                  </pre>
                </Box>
              )}

              {selectedScan.error_message && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom color="error">Error</Typography>
                  <Typography variant="body2" color="error">
                    {selectedScan.error_message}
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ScanHistory;