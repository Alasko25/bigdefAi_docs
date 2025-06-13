import React, { useState, useEffect } from 'react';
import { 
  CreditCard, 
  AlertTriangle, 
  Shield, 
  TrendingUp,
  Users,
  Building2,
  Activity,
  Brain
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useRealTimeData } from '../hooks/useRealTimeData';
import StatCard from '../components/Dashboard/StatCard';
import TransactionChart from '../components/Dashboard/TransactionChart';
import AlertsList from '../components/Dashboard/AlertsList';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { transactions, alerts, riskMetrics, loading } = useRealTimeData();
  const [chartData, setChartData] = useState<Array<{ date: string; transactions: number; fraud: number }>>([]);

  useEffect(() => {
    // Generate chart data from transactions
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date.toISOString().split('T')[0];
    });

    const data = last7Days.map(date => {
      const dayTransactions = transactions.filter(tx => 
        tx.timestamp.startsWith(date)
      );
      const fraudTransactions = dayTransactions.filter(tx => tx.fraudProbability > 0.7);
      
      return {
        date: new Date(date).toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' }),
        transactions: dayTransactions.length,
        fraud: fraudTransactions.length,
      };
    });

    setChartData(data);
  }, [transactions]);

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const totalTransactions = transactions.length;
  const fraudTransactions = transactions.filter(tx => tx.fraudProbability > 0.7).length;
  const blockedTransactions = transactions.filter(tx => tx.isBlocked).length;
  const activeAlerts = alerts.filter(a => a.status === 'open' || a.status === 'investigating').length;

  const fraudRate = totalTransactions > 0 ? fraudTransactions / totalTransactions : 0;
  const avgRiskScore = transactions.length > 0 
    ? transactions.reduce((sum, tx) => sum + tx.riskScore, 0) / transactions.length 
    : 0;

  const getWelcomeMessage = () => {
    switch (user?.role) {
      case 'admin':
        return 'Vue d\'ensemble du système';
      case 'analyst':
        return `Surveillance des fraudes - ${user.bankName}`;
      case 'client':
        return `Aperçu de votre compte - ${user.bankName}`;
      default:
        return 'Dashboard';
    }
  };

  const getStatsForRole = () => {
    const baseStats = [
      {
        title: 'Transactions Totales',
        value: totalTransactions.toLocaleString(),
        change: '+12% ce mois',
        changeType: 'positive' as const,
        icon: CreditCard,
        color: 'blue' as const,
      },
      {
        title: 'Fraudes Détectées',
        value: fraudTransactions.toLocaleString(),
        change: formatPercentage(fraudRate),
        changeType: fraudRate > 0.05 ? 'negative' as const : 'neutral' as const,
        icon: AlertTriangle,
        color: 'red' as const,
      },
    ];

    if (user?.role === 'admin') {
      return [
        ...baseStats,
        {
          title: 'Transactions Bloquées',
          value: blockedTransactions.toLocaleString(),
          change: '-5% ce mois',
          changeType: 'positive' as const,
          icon: Shield,
          color: 'green' as const,
        },
        {
          title: 'Alertes Actives',
          value: activeAlerts.toLocaleString(),
          change: 'Temps réel',
          changeType: 'neutral' as const,
          icon: Activity,
          color: 'yellow' as const,
        },
      ];
    }

    if (user?.role === 'analyst') {
      return [
        ...baseStats,
        {
          title: 'Score de Risque Moyen',
          value: (avgRiskScore * 100).toFixed(1) + '%',
          change: '-2.3% ce mois',
          changeType: 'positive' as const,
          icon: TrendingUp,
          color: 'purple' as const,
        },
        {
          title: 'Alertes à Traiter',
          value: activeAlerts.toLocaleString(),
          change: 'Urgent',
          changeType: 'negative' as const,
          icon: AlertTriangle,
          color: 'red' as const,
        },
      ];
    }

    // Client view
    return [
      {
        title: 'Mes Transactions',
        value: totalTransactions.toLocaleString(),
        change: '+3 cette semaine',
        changeType: 'neutral' as const,
        icon: CreditCard,
        color: 'blue' as const,
      },
      {
        title: 'Sécurité',
        value: fraudTransactions === 0 ? 'Sécurisé' : 'Attention',
        change: fraudTransactions === 0 ? 'Aucune fraude' : `${fraudTransactions} alertes`,
        changeType: fraudTransactions === 0 ? 'positive' as const : 'negative' as const,
        icon: Shield,
        color: fraudTransactions === 0 ? 'green' as const : 'red' as const,
      },
    ];
  };

  const stats = getStatsForRole();

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">{getWelcomeMessage()}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatCard key={index} {...stat} />
        ))}
      </div>

      {/* Charts and Lists */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {(user?.role === 'admin' || user?.role === 'analyst') && (
          <>
            <TransactionChart data={chartData} />
            <AlertsList alerts={alerts.slice(0, 5)} />
          </>
        )}
        
        {user?.role === 'client' && (
          <div className="lg:col-span-2">
            <TransactionChart data={chartData} />
          </div>
        )}
      </div>

      {/* AI Model Status (Admin only) */}
      {user?.role === 'admin' && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary-600" />
              État du Modèle IA
            </h3>
            <div className="flex items-center gap-2 px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              Actif
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">94.2%</div>
              <div className="text-sm text-gray-600">Précision</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">87.5%</div>
              <div className="text-sm text-gray-600">Rappel</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">45ms</div>
              <div className="text-sm text-gray-600">Temps de traitement</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">v2.1.3</div>
              <div className="text-sm text-gray-600">Version</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;