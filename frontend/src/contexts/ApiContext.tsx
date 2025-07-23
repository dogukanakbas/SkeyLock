import React, { createContext, useContext, ReactNode } from 'react';
import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:8002';
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Add request interceptor to include auth token
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

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

interface Scan {
  id: number;
  device_id: number;
  scan_type: string;
  status: string;
  started_at: string;
  completed_at?: string;
  results?: any;
  error_message?: string;
}

interface ApiContextType {
  // Devices
  getDevices: () => Promise<Device[]>;
  createDevice: (deviceData: any) => Promise<Device>;
  updateDevice: (id: number, deviceData: any) => Promise<Device>;
  deleteDevice: (id: number) => Promise<void>;
  
  // Scans
  getScans: () => Promise<Scan[]>;
  createScan: (scanData: any) => Promise<Scan>;
  getScan: (id: number) => Promise<Scan>;
  
  // Subscriptions
  getSubscriptionPlans: () => Promise<any[]>;
  getCurrentSubscription: () => Promise<any>;
  upgradeSubscription: (planName: string) => Promise<any>;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

export const useApi = () => {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
};

interface ApiProviderProps {
  children: ReactNode;
}

export const ApiProvider: React.FC<ApiProviderProps> = ({ children }) => {
  // Device API methods
  const getDevices = async (): Promise<Device[]> => {
    const response = await axios.get('/api/devices/');
    return response.data;
  };

  const createDevice = async (deviceData: any): Promise<Device> => {
    const response = await axios.post('/api/devices/', deviceData);
    return response.data;
  };

  const updateDevice = async (id: number, deviceData: any): Promise<Device> => {
    const response = await axios.put(`/api/devices/${id}`, deviceData);
    return response.data;
  };

  const deleteDevice = async (id: number): Promise<void> => {
    await axios.delete(`/api/devices/${id}`);
  };

  // Scan API methods
  const getScans = async (): Promise<Scan[]> => {
    const response = await axios.get('/api/scans/');
    return response.data;
  };

  const createScan = async (scanData: any): Promise<Scan> => {
    const response = await axios.post('/api/scans/', scanData);
    return response.data;
  };

  const getScan = async (id: number): Promise<Scan> => {
    const response = await axios.get(`/api/scans/${id}`);
    return response.data;
  };

  // Subscription API methods
  const getSubscriptionPlans = async (): Promise<any[]> => {
    const response = await axios.get('/api/subscriptions/plans');
    return response.data;
  };

  const getCurrentSubscription = async (): Promise<any> => {
    const response = await axios.get('/api/subscriptions/current');
    return response.data;
  };

  const upgradeSubscription = async (planName: string): Promise<any> => {
    const response = await axios.post(`/api/subscriptions/upgrade/${planName}`);
    return response.data;
  };

  const value = {
    getDevices,
    createDevice,
    updateDevice,
    deleteDevice,
    getScans,
    createScan,
    getScan,
    getSubscriptionPlans,
    getCurrentSubscription,
    upgradeSubscription
  };

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  );
};