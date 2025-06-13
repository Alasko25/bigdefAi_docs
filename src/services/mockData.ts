import { User, Transaction, FraudAlert, Bank, RiskMetrics, DashboardStats, AIModelMetrics } from '../types';

// Mock data for development and demo
export const mockUsers: User[] = [
  {
    id: '1',
    email: 'admin@bigdefend.ai',
    name: 'Admin BigDefend',
    role: 'admin',
    isActive: true,
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '2',
    email: 'analyst@bnp.fr',
    name: 'Jean Dupont',
    role: 'analyst',
    bankId: 'bnp',
    bankName: 'BNP Paribas',
    isActive: true,
    createdAt: '2024-01-02T00:00:00Z',
  },
  {
    id: '3',
    email: 'client@bnp.fr',
    name: 'Marie Martin',
    role: 'client',
    bankId: 'bnp',
    bankName: 'BNP Paribas',
    isActive: true,
    createdAt: '2024-01-03T00:00:00Z',
  },
];

export const mockBanks: Bank[] = [
  {
    id: 'bnp',
    name: 'BNP Paribas',
    code: 'BNP',
    country: 'France',
    isActive: true,
    totalTransactions: 15420,
    fraudRate: 0.023,
    riskLevel: 'medium',
  },
  {
    id: 'sg',
    name: 'Société Générale',
    code: 'SG',
    country: 'France',
    isActive: true,
    totalTransactions: 12350,
    fraudRate: 0.018,
    riskLevel: 'low',
  },
];

export const generateMockTransactions = (count: number = 50): Transaction[] => {
  const transactions: Transaction[] = [];
  const now = new Date();
  
  for (let i = 0; i < count; i++) {
    const timestamp = new Date(now.getTime() - Math.random() * 7 * 24 * 60 * 60 * 1000);
    const amount = Math.random() * 50000 + 100;
    const fraudProbability = Math.random();
    const riskScore = Math.random();
    
    transactions.push({
      id: `tx_${i + 1}`,
      amount,
      currency: 'EUR',
      timestamp: timestamp.toISOString(),
      fromAccount: `ACC${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`,
      toAccount: `ACC${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`,
      type: ['transfer', 'payment', 'withdrawal', 'deposit'][Math.floor(Math.random() * 4)] as any,
      status: fraudProbability > 0.8 ? 'flagged' : fraudProbability > 0.9 ? 'blocked' : 'completed',
      riskScore,
      fraudProbability,
      location: ['Paris, France', 'Lyon, France', 'Marseille, France', 'Toulouse, France'][Math.floor(Math.random() * 4)],
      deviceInfo: ['Mobile App - iOS', 'Web Browser - Chrome', 'Mobile App - Android', 'ATM'][Math.floor(Math.random() * 4)],
      bankId: mockBanks[Math.floor(Math.random() * mockBanks.length)].id,
      isBlocked: fraudProbability > 0.9,
      features: {},
    });
  }
  
  return transactions.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
};

export const generateMockAlerts = (transactions: Transaction[]): FraudAlert[] => {
  return transactions
    .filter(tx => tx.fraudProbability > 0.7)
    .map((tx, index) => ({
      id: `alert_${index + 1}`,
      transactionId: tx.id,
      bankId: tx.bankId,
      severity: tx.fraudProbability > 0.9 ? 'critical' : tx.fraudProbability > 0.8 ? 'high' : 'medium',
      type: 'Suspicious Transaction',
      description: `Transaction of ${tx.amount.toFixed(2)} ${tx.currency} flagged by AI model`,
      timestamp: tx.timestamp,
      status: tx.fraudProbability > 0.95 ? 'investigating' : 'open',
      fraudProbability: tx.fraudProbability,
      aiConfidence: Math.random() * 0.3 + 0.7,
      recommendedAction: tx.fraudProbability > 0.9 ? 'block' : tx.fraudProbability > 0.8 ? 'investigate' : 'review',
    }));
};

export const mockRiskMetrics: RiskMetrics = {
  totalTransactions: 15420,
  fraudDetected: 354,
  fraudRate: 0.023,
  averageRiskScore: 0.34,
  blockedTransactions: 89,
  falsePositives: 23,
  accuracy: 0.94,
  precision: 0.87,
  recall: 0.91,
  f1Score: 0.89,
};

export const mockDashboardStats: DashboardStats = {
  totalTransactions: 15420,
  fraudDetected: 354,
  fraudRate: 0.023,
  blockedTransactions: 89,
  activeAlerts: 47,
  totalUsers: 156,
  activeBanks: 12,
  systemHealth: 'healthy',
};

export const mockAIMetrics: AIModelMetrics = {
  modelVersion: 'v2.1.3',
  accuracy: 0.94,
  precision: 0.87,
  recall: 0.91,
  f1Score: 0.89,
  lastTraining: '2024-01-15T10:30:00Z',
  totalPredictions: 15420,
  averageProcessingTime: 45,
  status: 'active',
};

// Generate initial mock data
export const mockTransactions = generateMockTransactions(100);
export const mockAlerts = generateMockAlerts(mockTransactions);