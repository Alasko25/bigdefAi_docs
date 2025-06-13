export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'analyst' | 'client';
  bankId?: string;
  bankName?: string;
  isActive: boolean;
  createdAt: string;
}

export interface Transaction {
  id: string;
  amount: number;
  currency: string;
  timestamp: string;
  fromAccount: string;
  toAccount: string;
  type: 'transfer' | 'payment' | 'withdrawal' | 'deposit';
  status: 'pending' | 'completed' | 'flagged' | 'blocked';
  riskScore: number;
  fraudProbability: number;
  location: string;
  deviceInfo: string;
  bankId: string;
  isBlocked: boolean;
  blockedBy?: string;
  blockedAt?: string;
  features: Record<string, any>;
}

export interface FraudAlert {
  id: string;
  transactionId: string;
  bankId: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: string;
  description: string;
  timestamp: string;
  status: 'open' | 'investigating' | 'resolved' | 'false_positive';
  assignedTo?: string;
  fraudProbability: number;
  aiConfidence: number;
  recommendedAction: 'monitor' | 'review' | 'block' | 'investigate';
}

export interface Bank {
  id: string;
  name: string;
  code: string;
  country: string;
  isActive: boolean;
  totalTransactions: number;
  fraudRate: number;
  riskLevel: 'low' | 'medium' | 'high';
}

export interface RiskMetrics {
  totalTransactions: number;
  fraudDetected: number;
  fraudRate: number;
  averageRiskScore: number;
  blockedTransactions: number;
  falsePositives: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
}

export interface DashboardStats {
  totalTransactions: number;
  fraudDetected: number;
  fraudRate: number;
  blockedTransactions: number;
  activeAlerts: number;
  totalUsers: number;
  activeBanks: number;
  systemHealth: 'healthy' | 'warning' | 'critical';
}

export interface SimulationConfig {
  transactionCount: number;
  fraudRate: number;
  bankId: string;
  timeRange: 'realtime' | '1hour' | '1day';
  transactionTypes: string[];
  amountRange: {
    min: number;
    max: number;
  };
}

export interface AIModelMetrics {
  modelVersion: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  lastTraining: string;
  totalPredictions: number;
  averageProcessingTime: number;
  status: 'active' | 'training' | 'updating' | 'error';
}