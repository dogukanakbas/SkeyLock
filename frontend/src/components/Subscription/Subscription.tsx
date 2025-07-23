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
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Star,
  Business,
  Security,
  Devices,
  Support,
  Api,
  CloudSync,
  Shield
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext.tsx';
import { useApi } from '../../contexts/ApiContext.tsx';

interface SubscriptionPlan {
  name: string;
  price: number;
  features: string[];
  device_limit: number;
  stripe_price_id: string;
}

const Subscription: React.FC = () => {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [currentSubscription, setCurrentSubscription] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [upgradeDialogOpen, setUpgradeDialogOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);
  const { user } = useAuth();
  const { getSubscriptionPlans, getCurrentSubscription, upgradeSubscription } = useApi();

  useEffect(() => {
    fetchSubscriptionData();
  }, []);

  const fetchSubscriptionData = async () => {
    try {
      // Mock data for demo
      setPlans([
        {
          name: 'Starter',
          price: 29,
          device_limit: 50,
          stripe_price_id: 'price_starter',
          features: [
            'Up to 50 devices',
            'Basic security scans',
            'Email support',
            'Monthly reports',
            'Basic vulnerability detection'
          ]
        },
        {
          name: 'Professional',
          price: 99,
          device_limit: -1,
          stripe_price_id: 'price_professional',
          features: [
            'Unlimited devices',
            'Advanced security scans',
            'Real-time monitoring',
            'API access',
            'Priority support',
            'Custom reports',
            'Advanced vulnerability detection',
            'Compliance reporting'
          ]
        },
        {
          name: 'Enterprise',
          price: 299,
          device_limit: -1,
          stripe_price_id: 'price_enterprise',
          features: [
            'Everything in Professional',
            'Multi-location support',
            'Custom integrations',
            'Dedicated support manager',
            'White-label dashboard',
            'Advanced analytics',
            'Custom security policies',
            'SLA guarantee'
          ]
        }
      ]);

      setCurrentSubscription({
        plan_type: user?.subscription_plan || 'demo',
        status: user?.subscription_status || 'trial',
        current_period_start: '2024-01-15T00:00:00Z',
        current_period_end: '2024-01-22T00:00:00Z',
        trial_days_left: user?.trial_days_left || 0
      });
    } catch (error) {
      console.error('Failed to fetch subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (plan: SubscriptionPlan) => {
    setSelectedPlan(plan);
    setUpgradeDialogOpen(true);
  };

  const confirmUpgrade = async () => {
    if (!selectedPlan) return;
    
    try {
      const result = await upgradeSubscription(selectedPlan.name.toLowerCase());
      // Redirect to Stripe checkout
      window.location.href = result.checkout_url;
    } catch (error) {
      console.error('Failed to upgrade subscription:', error);
      alert('Failed to upgrade subscription. Please try again.');
    }
    setUpgradeDialogOpen(false);
  };

  const getPlanIcon = (planName: string) => {
    switch (planName.toLowerCase()) {
      case 'starter':
        return <Star color="primary" />;
      case 'professional':
        return <Business color="secondary" />;
      case 'enterprise':
        return <Shield color="action" />;
      default:
        return <Security />;
    }
  };

  const getStatusChip = (status: string) => {
    const statusConfig: { [key: string]: { color: 'success' | 'warning' | 'error' | 'info', label: string } } = {
      active: { color: 'success', label: 'Active' },
      trial: { color: 'warning', label: 'Trial' },
      expired: { color: 'error', label: 'Expired' },
      canceled: { color: 'error', label: 'Canceled' }
    };
    const config = statusConfig[status] || { color: 'info', label: status };
    return <Chip label={config.label} color={config.color} size="small" />;
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Subscription Management
      </Typography>

      {/* Current Subscription Status */}
      {currentSubscription && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {getPlanIcon(currentSubscription.plan_type)}
                  <Box>
                    <Typography variant="h6">
                      Current Plan: {currentSubscription.plan_type.toUpperCase()}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                      <Typography variant="body2" color="textSecondary">
                        Status:
                      </Typography>
                      {getStatusChip(currentSubscription.status)}
                    </Box>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                {currentSubscription.plan_type === 'demo' && (
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      Your trial expires in {currentSubscription.trial_days_left} days.
                      Upgrade now to continue using all features.
                    </Typography>
                  </Alert>
                )}
                <Typography variant="body2" color="textSecondary">
                  {currentSubscription.status === 'active' ? 'Next billing:' : 'Trial ends:'} {' '}
                  {new Date(currentSubscription.current_period_end).toLocaleDateString()}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Subscription Plans */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Choose Your Plan
      </Typography>

      <Grid container spacing={3}>
        {plans.map((plan) => (
          <Grid item xs={12} md={4} key={plan.name}>
            <Card 
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                ...(plan.name === 'Professional' && {
                  border: '2px solid',
                  borderColor: 'primary.main'
                })
              }}
            >
              {plan.name === 'Professional' && (
                <Chip
                  label="Most Popular"
                  color="primary"
                  size="small"
                  sx={{
                    position: 'absolute',
                    top: 16,
                    right: 16,
                    zIndex: 1
                  }}
                />
              )}
              
              <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                  {getPlanIcon(plan.name)}
                  <Typography variant="h5" component="h2" sx={{ mt: 1, mb: 1 }}>
                    {plan.name}
                  </Typography>
                  <Typography variant="h3" color="primary" sx={{ mb: 1 }}>
                    ${plan.price}
                    <Typography component="span" variant="h6" color="textSecondary">
                      /month
                    </Typography>
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {plan.device_limit === -1 ? 'Unlimited devices' : `Up to ${plan.device_limit} devices`}
                  </Typography>
                </Box>

                <List dense sx={{ flexGrow: 1 }}>
                  {plan.features.map((feature, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <CheckCircle color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={feature}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>

                <Divider sx={{ my: 2 }} />

                <Button
                  variant={plan.name === 'Professional' ? 'contained' : 'outlined'}
                  color="primary"
                  fullWidth
                  size="large"
                  onClick={() => handleUpgrade(plan)}
                  disabled={currentSubscription?.plan_type === plan.name.toLowerCase()}
                >
                  {currentSubscription?.plan_type === plan.name.toLowerCase() 
                    ? 'Current Plan' 
                    : currentSubscription?.plan_type === 'demo' 
                      ? 'Start Free Trial' 
                      : 'Upgrade'}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Features Comparison */}
      <Box sx={{ mt: 6 }}>
        <Typography variant="h5" gutterBottom>
          Feature Comparison
        </Typography>
        <Card>
          <CardContent>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Typography variant="h6" gutterBottom>Features</Typography>
                <List dense>
                  <ListItem><ListItemText primary="Device Monitoring" /></ListItem>
                  <ListItem><ListItemText primary="Security Scans" /></ListItem>
                  <ListItem><ListItemText primary="Vulnerability Detection" /></ListItem>
                  <ListItem><ListItemText primary="API Access" /></ListItem>
                  <ListItem><ListItemText primary="Priority Support" /></ListItem>
                  <ListItem><ListItemText primary="Custom Reports" /></ListItem>
                  <ListItem><ListItemText primary="Multi-location" /></ListItem>
                  <ListItem><ListItemText primary="White-label" /></ListItem>
                </List>
              </Grid>
              
              {plans.map((plan) => (
                <Grid item xs={12} md={3} key={plan.name}>
                  <Typography variant="h6" gutterBottom align="center">
                    {plan.name}
                  </Typography>
                  <List dense>
                    <ListItem sx={{ justifyContent: 'center' }}>
                      <CheckCircle color="success" />
                    </ListItem>
                    <ListItem sx={{ justifyContent: 'center' }}>
                      <CheckCircle color="success" />
                    </ListItem>
                    <ListItem sx={{ justifyContent: 'center' }}>
                      {plan.name !== 'Starter' ? <CheckCircle color="success" /> : <Cancel color="disabled" />}
                    </ListItem>
                    <ListItem sx={{ justifyContent: 'center' }}>
                      {plan.name === 'Professional' || plan.name === 'Enterprise' ? <CheckCircle color="success" /> : <Cancel color="disabled" />}
                    </ListItem>
                    <ListItem sx={{ justifyContent: 'center' }}>
                      {plan.name === 'Professional' || plan.name === 'Enterprise' ? <CheckCircle color="success" /> : <Cancel color="disabled" />}
                    </ListItem>
                    <ListItem sx={{ justifyContent: 'center' }}>
                      {plan.name === 'Professional' || plan.name === 'Enterprise' ? <CheckCircle color="success" /> : <Cancel color="disabled" />}
                    </ListItem>
                    <ListItem sx={{ justifyContent: 'center' }}>
                      {plan.name === 'Enterprise' ? <CheckCircle color="success" /> : <Cancel color="disabled" />}
                    </ListItem>
                    <ListItem sx={{ justifyContent: 'center' }}>
                      {plan.name === 'Enterprise' ? <CheckCircle color="success" /> : <Cancel color="disabled" />}
                    </ListItem>
                  </List>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Box>

      {/* Upgrade Confirmation Dialog */}
      <Dialog open={upgradeDialogOpen} onClose={() => setUpgradeDialogOpen(false)}>
        <DialogTitle>Confirm Upgrade</DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            Are you sure you want to upgrade to the {selectedPlan?.name} plan?
          </Typography>
          <Typography variant="body2" color="textSecondary">
            You will be redirected to Stripe to complete the payment process.
          </Typography>
          {selectedPlan && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="subtitle2">Plan Details:</Typography>
              <Typography variant="body2">
                {selectedPlan.name} - ${selectedPlan.price}/month
              </Typography>
              <Typography variant="body2">
                {selectedPlan.device_limit === -1 ? 'Unlimited devices' : `Up to ${selectedPlan.device_limit} devices`}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpgradeDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmUpgrade} variant="contained">
            Continue to Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Subscription;