import axios from 'axios';
import { User, Transaction, FraudAlert, Bank, RiskMetrics, DashboardStats, SimulationConfig, AIModelMetrics } from '../types';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  
  logout: async () => {
    await api.post('/auth/logout');
    localStorage.removeItem('auth_token');
  },
  
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Users API
export const usersAPI = {
  getUsers: async (): Promise<User[]> => {
    const response = await api.get('/users');
    return response.data;
  },
  
  createUser: async (userData: Partial<User>): Promise<User> => {
    const response = await api.post('/users', userData);
    return response.data;
  },
  
  updateUser: async (id: string, userData: Partial<User>): Promise<User> => {
    const response = await api.put(`/users/${id}`, userData);
    return response.data;
  },
  
  deleteUser: async (id: string): Promise<void> => {
    await api.delete(`/users/${id}`);
  },
};

// Transactions API
export const transactionsAPI = {
  getTransactions: async (bankId?: string): Promise<Transaction[]> => {
    const url = bankId ? `/transactions/bank/${bankId}` : '/transactions';
    const response = await api.get(url);
    return response.data;
  },
  
  getTransaction: async (id: string): Promise<Transaction> => {
    const response = await api.get(`/transactions/${id}`);
    return response.data;
  },
  
  blockTransaction: async (id: string, reason: string): Promise<Transaction> => {
    const response = await api.post(`/transactions/${id}/block`, { reason });
    return response.data;
  },
  
  unblockTransaction: async (id: string): Promise<Transaction> => {
    const response = await api.post(`/transactions/${id}/unblock`);
    return response.data;
  },
  
  analyzeTransaction: async (transactionData: Partial<Transaction>): Promise<{ fraudProbability: number; riskScore: number; recommendation: string }> => {
    const response = await api.post('/transactions/analyze', transactionData);
    return response.data;
  },
};

// Alerts API
export const alertsAPI = {
  getAlerts: async (bankId?: string): Promise<FraudAlert[]> => {
    const url = bankId ? `/alerts/bank/${bankId}` : '/alerts';
    const response = await api.get(url);
    return response.data;
  },
  
  updateAlertStatus: async (id: string, status: string, assignedTo?: string): Promise<FraudAlert> => {
    const response = await api.put(`/alerts/${id}/status`, { status, assignedTo });
    return response.data;
  },
  
  getAlert: async (id: string): Promise<FraudAlert> => {
    const response = await api.get(`/alerts/${id}`);
    return response.data;
  },
};

// Banks API
export const banksAPI = {
  getBanks: async (): Promise<Bank[]> => {
    const response = await api.get('/banks');
    return response.data;
  },
  
  createBank: async (bankData: Partial<Bank>): Promise<Bank> => {
    const response = await api.post('/banks', bankData);
    return response.data;
  },
  
  updateBank: async (id: string, bankData: Partial<Bank>): Promise<Bank> => {
    const response = await api.put(`/banks/${id}`, bankData);
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: async (bankId?: string): Promise<DashboardStats> => {
    const url = bankId ? `/dashboard/stats/${bankId}` : '/dashboard/stats';
    const response = await api.get(url);
    return response.data;
  },
  
  getRiskMetrics: async (bankId?: string): Promise<RiskMetrics> => {
    const url = bankId ? `/dashboard/metrics/${bankId}` : '/dashboard/metrics';
    const response = await api.get(url);
    return response.data;
  },
  
  getAIMetrics: async (): Promise<AIModelMetrics> => {
    const response = await api.get('/dashboard/ai-metrics');
    return response.data;
  },
};

// Simulation API
export const simulationAPI = {
  startSimulation: async (config: SimulationConfig): Promise<{ simulationId: string }> => {
    const response = await api.post('/simulation/start', config);
    return response.data;
  },
  
  stopSimulation: async (simulationId: string): Promise<void> => {
    await api.post(`/simulation/${simulationId}/stop`);
  },
  
  getSimulationStatus: async (simulationId: string): Promise<{ status: string; progress: number }> => {
    const response = await api.get(`/simulation/${simulationId}/status`);
    return response.data;
  },
};

// Health check
export const healthCheck = async (): Promise<boolean> => {
  try {
    await api.get('/health');
    return true;
  } catch {
    return false;
  }
};

export default api;