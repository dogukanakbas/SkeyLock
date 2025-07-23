import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton
} from '@mui/material';
import {
  Add,
  Security,
  NetworkCheck,
  Warning,
  CheckCircle,
  Error,
  Refresh
} from '@mui/icons-material';
import { useApi } from '../../contexts/ApiContext.tsx';

interface Device {
  id: number;
  ip_address: string;
  mac_address?: string;
  hostname?: string;
  device_type?: string;
  manufacturer?: string;
  model?: string;
  firmware_version?: string;
  first_seen: string;
  last_seen: string;
  is_active: boolean;
  risk_score: number;
  open_ports_count: number;
  vulnerabilities_count: number;
  critical_vulnerabilities: number;
}

const DeviceList: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newDevice, setNewDevice] = useState({
    ip_address: '',
    hostname: '',
    device_type: ''
  });
  const { getDevices, createDevice, createScan } = useApi();

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    try {
      const deviceData = await getDevices();
      setDevices(deviceData);
    } catch (error) {
      console.error('Failed to fetch devices:', error);
      // Mock data for demo
      setDevices([
        {
          id: 1,
          ip_address: '192.168.1.100',
          hostname: 'smart-camera-01',
          device_type: 'IP Camera',
          manufacturer: 'Hikvision',
          model: 'DS-2CD2043G0-I',
          firmware_version: '5.6.3',
          first_seen: '2024-01-15T10:00:00Z',
          last_seen: '2024-01-21T14:30:00Z',
          is_active: true,
          risk_score: 75.5,
          open_ports_count: 3,
          vulnerabilities_count: 2,
          critical_vulnerabilities: 1,
          mac_address: '00:11:22:33:44:55'
        },
        {
          id: 2,
          ip_address: '192.168.1.101',
          hostname: 'smart-thermostat',
          device_type: 'Thermostat',
          manufacturer: 'Nest',
          model: 'Learning Thermostat',
          firmware_version: '6.0.0',
          first_seen: '2024-01-10T09:00:00Z',
          last_seen: '2024-01-21T14:25:00Z',
          is_active: true,
          risk_score: 25.0,
          open_ports_count: 1,
          vulnerabilities_count: 0,
          critical_vulnerabilities: 0,
          mac_address: '00:11:22:33:44:66'
        },
        {
          id: 3,
          ip_address: '192.168.1.102',
          hostname: 'smart-doorbell',
          device_type: 'Doorbell',
          manufacturer: 'Ring',
          model: 'Video Doorbell Pro',
          firmware_version: '1.4.26',
          first_seen: '2024-01-12T11:00:00Z',
          last_seen: '2024-01-21T14:20:00Z',
          is_active: false,
          risk_score: 45.0,
          open_ports_count: 2,
          vulnerabilities_count: 1,
          critical_vulnerabilities: 0,
          mac_address: '00:11:22:33:44:77'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddDevice = async () => {
    try {
      await createDevice(newDevice);
      setAddDialogOpen(false);
      setNewDevice({ ip_address: '', hostname: '', device_type: '' });
      fetchDevices();
    } catch (error) {
      console.error('Failed to add device:', error);
    }
  };

  const handleStartScan = async (deviceId: number) => {
    try {
      console.log(`Starting scan for device ${deviceId}`);
      const scanResult = await createScan({
        device_id: deviceId,
        scan_type: 'quick'
      });
      console.log('Scan started:', scanResult);
      
      // Show success message
      alert(`Scan started successfully! Scan ID: ${scanResult.id}`);
      
      // Refresh devices to update last scan info
      setTimeout(() => {
        fetchDevices();
      }, 2000);
      
    } catch (error) {
      console.error('Failed to start scan:', error);
      alert('Failed to start scan. Please try again.');
    }
  };

  const getRiskChip = (riskScore: number) => {
    if (riskScore >= 70) {
      return <Chip label="High Risk" color="error" size="small" icon={<Error />} />;
    } else if (riskScore >= 40) {
      return <Chip label="Medium Risk" color="warning" size="small" icon={<Warning />} />;
    } else {
      return <Chip label="Low Risk" color="success" size="small" icon={<CheckCircle />} />;
    }
  };

  const getStatusChip = (isActive: boolean) => {
    return isActive ? (
      <Chip label="Online" color="success" size="small" />
    ) : (
      <Chip label="Offline" color="error" size="small" />
    );
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          IoT Devices ({devices.length})
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchDevices}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddDialogOpen(true)}
          >
            Add Device
          </Button>
        </Box>
      </Box>

      {/* Device Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Devices
              </Typography>
              <Typography variant="h4">
                {devices.filter(d => d.is_active).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                High Risk
              </Typography>
              <Typography variant="h4" color="error">
                {devices.filter(d => d.risk_score >= 70).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Critical Vulnerabilities
              </Typography>
              <Typography variant="h4" color="error">
                {devices.reduce((sum, d) => sum + d.critical_vulnerabilities, 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Open Ports
              </Typography>
              <Typography variant="h4">
                {devices.reduce((sum, d) => sum + d.open_ports_count, 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Devices Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Device</TableCell>
                  <TableCell>IP Address</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Risk Level</TableCell>
                  <TableCell>Vulnerabilities</TableCell>
                  <TableCell>Last Seen</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {devices.map((device) => (
                  <TableRow key={device.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle2">
                          {device.hostname || 'Unknown Device'}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {device.manufacturer} {device.model}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{device.ip_address}</TableCell>
                    <TableCell>{device.device_type || 'Unknown'}</TableCell>
                    <TableCell>{getStatusChip(device.is_active)}</TableCell>
                    <TableCell>{getRiskChip(device.risk_score)}</TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {device.vulnerabilities_count} total
                        </Typography>
                        {device.critical_vulnerabilities > 0 && (
                          <Typography variant="caption" color="error">
                            {device.critical_vulnerabilities} critical
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      {new Date(device.last_seen).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<Security />}
                        onClick={() => handleStartScan(device.id)}
                      >
                        Scan
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Add Device Dialog */}
      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Device</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="IP Address"
            type="text"
            fullWidth
            variant="outlined"
            value={newDevice.ip_address}
            onChange={(e) => setNewDevice({ ...newDevice, ip_address: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Hostname"
            type="text"
            fullWidth
            variant="outlined"
            value={newDevice.hostname}
            onChange={(e) => setNewDevice({ ...newDevice, hostname: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Device Type"
            type="text"
            fullWidth
            variant="outlined"
            value={newDevice.device_type}
            onChange={(e) => setNewDevice({ ...newDevice, device_type: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddDevice} variant="contained">Add Device</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DeviceList;