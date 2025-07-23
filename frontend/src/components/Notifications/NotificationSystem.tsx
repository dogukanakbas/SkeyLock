import React, { useState, useEffect } from 'react';
import {
  IconButton,
  Badge,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  Divider,
} from '@mui/material';
import {
  Notifications,
  Security,
  Warning,
  Info,
  BugReport,
  Router,
} from '@mui/icons-material';

interface Notification {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  category: 'scan' | 'vulnerability' | 'device' | 'system';
}

interface NotificationSystemProps {
  onNotificationClick?: (notification: Notification) => void;
}

const NotificationSystem: React.FC<NotificationSystemProps> = ({ onNotificationClick }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // Simulate some initial notifications
  useEffect(() => {
    const initialNotifications: Notification[] = [
      {
        id: '1',
        type: 'warning',
        title: 'Vulnerability Detected',
        message: 'Medium risk vulnerability found on device 192.168.1.100',
        category: 'vulnerability',
        timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
        read: false,
      },
      {
        id: '2',
        type: 'success',
        title: 'Scan Completed',
        message: 'Security scan finished successfully on 5 devices',
        category: 'scan',
        timestamp: new Date(Date.now() - 15 * 60 * 1000), // 15 minutes ago
        read: false,
      },
      {
        id: '3',
        type: 'info',
        title: 'New Device Discovered',
        message: 'Smart doorbell detected on network',
        category: 'device',
        timestamp: new Date(Date.now() - 60 * 60 * 1000), // 1 hour ago
        read: true,
      },
    ];
    
    setNotifications(initialNotifications);
  }, []);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
    // Mark all as read when opening menu
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = (notification: Notification) => {
    if (onNotificationClick) {
      onNotificationClick(notification);
    }
    handleMenuClose();
  };

  const getNotificationIcon = (category: string) => {
    switch (category) {
      case 'scan': return <Security fontSize="small" />;
      case 'vulnerability': return <BugReport fontSize="small" />;
      case 'device': return <Router fontSize="small" />;
      case 'system': return <Info fontSize="small" />;
      default: return <Info fontSize="small" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success': return '#4caf50';
      case 'warning': return '#ff9800';
      case 'error': return '#f44336';
      case 'info': return '#2196f3';
      default: return '#9e9e9e';
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <>
      {/* Notification Bell */}
      <IconButton
        color="inherit"
        onClick={handleMenuOpen}
        title="Notifications"
      >
        <Badge badgeContent={unreadCount} color="error">
          <Notifications />
        </Badge>
      </IconButton>

      {/* Notification Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: { width: 350, maxHeight: 400 }
        }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">Notifications</Typography>
          <Typography variant="body2" color="text.secondary">
            {notifications.length} total notifications
          </Typography>
        </Box>
        
        {notifications.length === 0 ? (
          <MenuItem>
            <Typography variant="body2" color="text.secondary">
              No notifications
            </Typography>
          </MenuItem>
        ) : (
          notifications.slice(0, 10).map((notification, index) => (
            <React.Fragment key={notification.id}>
              <MenuItem
                onClick={() => handleNotificationClick(notification)}
                sx={{
                  py: 1.5,
                  backgroundColor: notification.read ? 'transparent' : 'action.hover',
                }}
              >
                <ListItemIcon sx={{ color: getNotificationColor(notification.type) }}>
                  {getNotificationIcon(notification.category)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="subtitle2" noWrap>
                      {notification.title}
                    </Typography>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary" noWrap>
                        {notification.message}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {notification.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Box>
                  }
                />
              </MenuItem>
              {index < Math.min(notifications.length - 1, 9) && <Divider />}
            </React.Fragment>
          ))
        )}
      </Menu>
    </>
  );
};

export default NotificationSystem;