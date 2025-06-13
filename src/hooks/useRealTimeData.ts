import { useState, useEffect, useCallback } from 'react';
import { Transaction, FraudAlert, RiskMetrics } from '../types';
import { transactionsAPI, alertsAPI, dashboardAPI } from '../services/api';
import { wsService } from '../services/websocket';
import { useAuth } from '../contexts/AuthContext';
import { mockTransactions, mockAlerts, mockRiskMetrics } from '../services/mockData';

export const useRealTimeData = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const loadInitialData = useCallback(async () => {
    if (!user) return;

    try {
      setLoading(true);
      setError(null);

      const bankId = user.role === 'admin' ? undefined : user.bankId;

      // Try to load real data
      try {
        const [txns, alts, metrics] = await Promise.all([
          transactionsAPI.getTransactions(bankId),
          alertsAPI.getAlerts(bankId),
          dashboardAPI.getRiskMetrics(bankId),
        ]);

        setTransactions(txns);
        setAlerts(alts);
        setRiskMetrics(metrics);
      } catch (apiError) {
        // Fallback to mock data
        console.log('Using mock data for demo');
        const filteredTransactions = bankId 
          ? mockTransactions.filter(tx => tx.bankId === bankId)
          : mockTransactions;
        const filteredAlerts = bankId
          ? mockAlerts.filter(alert => alert.bankId === bankId)
          : mockAlerts;

        setTransactions(filteredTransactions);
        setAlerts(filteredAlerts);
        setRiskMetrics(mockRiskMetrics);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (!user) return;

    const token = localStorage.getItem('auth_token');
    if (!token || token.startsWith('mock_token')) {
      loadInitialData();
      return;
    }

    // WebSocket event handlers
    const handleNewTransaction = (transaction: Transaction) => {
      console.log('New transaction received:', transaction);
      setTransactions(prev => [transaction, ...prev.slice(0, 99)]);
    };

    const handleFraudAlert = (alert: FraudAlert) => {
      console.log('Fraud alert received:', alert);
      setAlerts(prev => [alert, ...prev]);
    };

    const handleRiskUpdate = (metrics: RiskMetrics) => {
      console.log('Risk metrics updated:', metrics);
      setRiskMetrics(metrics);
    };

    const handleConnected = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    const handleDisconnected = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    const handleError = (error: any) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    // Register WebSocket event listeners
    wsService.on('newTransaction', handleNewTransaction);
    wsService.on('fraudAlert', handleFraudAlert);
    wsService.on('riskUpdate', handleRiskUpdate);
    wsService.on('connected', handleConnected);
    wsService.on('disconnected', handleDisconnected);
    wsService.on('error', handleError);

    // Connect WebSocket
    wsService.connect(token);

    // Load initial data
    loadInitialData();

    // Cleanup
    return () => {
      wsService.off('newTransaction', handleNewTransaction);
      wsService.off('fraudAlert', handleFraudAlert);
      wsService.off('riskUpdate', handleRiskUpdate);
      wsService.off('connected', handleConnected);
      wsService.off('disconnected', handleDisconnected);
      wsService.off('error', handleError);
      wsService.disconnect();
    };
  }, [user, loadInitialData]);

  const updateAlert = useCallback(async (alertId: string, status: string, assignedTo?: string) => {
    try {
      const updatedAlert = await alertsAPI.updateAlertStatus(alertId, status, assignedTo);
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId ? updatedAlert : alert
      ));
    } catch (error) {
      console.error('Failed to update alert:', error);
      // For demo, update locally
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId ? { ...alert, status: status as any, assignedTo } : alert
      ));
    }
  }, []);

  const blockTransaction = useCallback(async (transactionId: string, reason: string) => {
    try {
      const updatedTransaction = await transactionsAPI.blockTransaction(transactionId, reason);
      setTransactions(prev => prev.map(tx => 
        tx.id === transactionId ? updatedTransaction : tx
      ));
    } catch (error) {
      console.error('Failed to block transaction:', error);
      // For demo, update locally
      setTransactions(prev => prev.map(tx => 
        tx.id === transactionId 
          ? { ...tx, status: 'blocked', isBlocked: true, blockedBy: user?.name, blockedAt: new Date().toISOString() }
          : tx
      ));
    }
  }, [user]);

  const unblockTransaction = useCallback(async (transactionId: string) => {
    try {
      const updatedTransaction = await transactionsAPI.unblockTransaction(transactionId);
      setTransactions(prev => prev.map(tx => 
        tx.id === transactionId ? updatedTransaction : tx
      ));
    } catch (error) {
      console.error('Failed to unblock transaction:', error);
      // For demo, update locally
      setTransactions(prev => prev.map(tx => 
        tx.id === transactionId 
          ? { ...tx, status: 'completed', isBlocked: false, blockedBy: undefined, blockedAt: undefined }
          : tx
      ));
    }
  }, []);

  return {
    transactions,
    alerts,
    riskMetrics,
    loading,
    error,
    isConnected,
    refreshData: loadInitialData,
    updateAlert,
    blockTransaction,
    unblockTransaction,
  };
};