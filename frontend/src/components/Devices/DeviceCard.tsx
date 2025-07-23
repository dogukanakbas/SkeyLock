import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  LinearProgress,
  Avatar,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  MoreVert,
  Security,
  NetworkCheck,
  Warning,
  CheckCircle,
  Error,
  Edit,
  Delete,
  PlayArrow,
  Stop,
  Router,
  Wifi,
  WifiOff,
} from '@mui/icons-material';

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

interface DeviceCardProps {
  device: Device;
  onScan: (deviceId: number) => void;
  onEdit: (device: Device) => void;
  onDelete: (deviceId: number) => void;
}

const DeviceCard: React.FC<DeviceCardProps> = ({ device, onScan, onEdit, onDelete }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [scanning, setScanning] = useState(false);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleScan = async () => {
    setScanning(true);
    try {
      await onScan(device.id);
    } finally {
      setScanning(false);
    }
    handleMenuClose();
  };

  const handleEdit = () => {
    onEdit(device);
    handleMenuClose();
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  const handleDeleteConfirm = () => {
    onDelete(device.id);
    setDeleteDialogOpen(false);
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

  const getDeviceIcon = (type?: string) => {
    switch (type?.toLowerCase()) {
      case 'camera':
      case 'ip camera':
        return '📹';
      case 'thermostat':
        return '🌡️';
      case 'doorbell':
        return '🔔';
      case 'router':
        return '📡';
      case 'smart tv':
        return '📺';
      case 'speaker':
        return '🔊';
      default:
        return '🔌';
    }
  };

  const timeSinceLastSeen = () => {
    const lastSeen = new Date(device.last_seen);
    const now = new Date();
    const diffMs = now.getTime() - lastSeen.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  return (
    <>
      <Card 
        sx={{ 
          height: '100%', 
          display: 'flex', 
          flexDirection: 'column',
          position: 'relative',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: 4,
          }
        }}
      >
        {/* Status Indicator */}
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            width: 12,
            height: 12,
            borderRadius: '50%',
            backgroundColor: device.is_active ? '#4caf50' : '#f44336',
            boxShadow: `0 0 0 2px ${device.is_active ? '#4caf50' : '#f44336'}33`,
          }}
        />

        <CardContent sx={{ flexGrow: 1, pb: 1 }}>
          {/* Device Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
              {getDeviceIcon(device.device_type)}
            </Avatar>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" component="div" noWrap>
                {device.hostname || 'Unknown Device'}
              </Typography>
              <Typography variant="body2" color="text.secondary" noWrap>
                {device.ip_address}
              </Typography>
            </Box>
            <IconButton size="small" onClick={handleMenuOpen}>
              <MoreVert />
            </IconButton>
          </Box>

          {/* Device Info */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {device.manufacturer} {device.model}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Type: {device.device_type || 'Unknown'}
            </Typography>
          </Box>

          {/* Risk Score */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2">Risk Score</Typography>
              <Chip 
                label={getRiskLabel(device.risk_score)}
                color={getRiskColor(device.risk_score)}
                size="small"
              />
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={device.risk_score} 
              color={getRiskColor(device.risk_score)}
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>

          {/* Stats */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Tooltip title="Open Ports">
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <NetworkCheck fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
                <Typography variant="body2">{device.open_ports_count}</Typography>
              </Box>
            </Tooltip>
            <Tooltip title="Vulnerabilities">
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Warning fontSize="small" sx={{ mr: 0.5, color: 'warning.main' }} />
                <Typography variant="body2">{device.vulnerabilities_count}</Typography>
              </Box>
            </Tooltip>
            <Tooltip title="Critical Issues">
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Error fontSize="small" sx={{ mr: 0.5, color: 'error.main' }} />
                <Typography variant="body2">{device.critical_vulnerabilities}</Typography>
              </Box>
            </Tooltip>
          </Box>

          {/* Last Seen */}
          <Typography variant="caption" color="text.secondary">
            Last seen: {timeSinceLastSeen()}
          </Typography>
        </CardContent>

        <CardActions sx={{ pt: 0 }}>
          <Button
            size="small"
            variant="contained"
            startIcon={scanning ? <Stop /> : <Security />}
            onClick={handleScan}
            disabled={scanning}
            fullWidth
          >
            {scanning ? 'Scanning...' : 'Quick Scan'}
          </Button>
        </CardActions>

        {scanning && (
          <LinearProgress 
            sx={{ 
              position: 'absolute', 
              bottom: 0, 
              left: 0, 
              right: 0,
              borderBottomLeftRadius: 4,
              borderBottomRightRadius: 4,
            }} 
          />
        )}
      </Card>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleScan} disabled={scanning}>
          <Security fontSize="small" sx={{ mr: 1 }} />
          {scanning ? 'Scanning...' : 'Start Scan'}
        </MenuItem>
        <MenuItem onClick={handleEdit}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Edit Device
        </MenuItem>
        <MenuItem onClick={handleDeleteClick} sx={{ color: 'error.main' }}>
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Delete Device
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Device</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{device.hostname || device.ip_address}"? 
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DeviceCard;