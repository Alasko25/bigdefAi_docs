import React, { useState } from 'react';
import { 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Shield, 
  ShieldOff,
  AlertTriangle,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useRealTimeData } from '../hooks/useRealTimeData';
import { Transaction } from '../types';
import { formatCurrency, formatDate, getRiskColor, getStatusColor } from '../utils/formatters';

const Transactions: React.FC = () => {
  const { user } = useAuth();
  const { transactions, loading, blockTransaction, unblockTransaction } = useRealTimeData();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);

  const filteredTransactions = transactions.filter(tx => {
    const matchesSearch = 
      tx.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tx.fromAccount.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tx.toAccount.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || tx.status === statusFilter;
    
    const matchesRisk = 
      riskFilter === 'all' ||
      (riskFilter === 'high' && tx.fraudProbability > 0.7) ||
      (riskFilter === 'medium' && tx.fraudProbability > 0.4 && tx.fraudProbability <= 0.7) ||
      (riskFilter === 'low' && tx.fraudProbability <= 0.4);

    return matchesSearch && matchesStatus && matchesRisk;
  });

  const handleBlockTransaction = async (transactionId: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir bloquer cette transaction ?')) {
      await blockTransaction(transactionId, 'Blocked by analyst due to fraud suspicion');
    }
  };

  const handleUnblockTransaction = async (transactionId: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir débloquer cette transaction ?')) {
      await unblockTransaction(transactionId);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      case 'pending':
        return <Clock className="h-4 w-4" />;
      case 'flagged':
        return <AlertTriangle className="h-4 w-4" />;
      case 'blocked':
        return <XCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
          <p className="text-gray-600 mt-1">
            {user?.role === 'client' ? 'Vos transactions' : 'Surveillance des transactions'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-secondary flex items-center gap-2">
            <Download className="h-4 w-4" />
            Exporter
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Rechercher par ID, compte..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10 w-full"
              />
            </div>
          </div>
          
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input w-auto"
          >
            <option value="all">Tous les statuts</option>
            <option value="completed">Complétées</option>
            <option value="pending">En attente</option>
            <option value="flagged">Signalées</option>
            <option value="blocked">Bloquées</option>
          </select>

          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="input w-auto"
          >
            <option value="all">Tous les risques</option>
            <option value="high">Risque élevé</option>
            <option value="medium">Risque moyen</option>
            <option value="low">Risque faible</option>
          </select>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Transaction
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Montant
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risque
                </th>
                {(user?.role === 'admin' || user?.role === 'analyst') && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                )}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTransactions.map((transaction) => (
                <tr key={transaction.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {transaction.id}
                      </div>
                      <div className="text-sm text-gray-500">
                        {transaction.fromAccount} → {transaction.toAccount}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {formatCurrency(transaction.amount, transaction.currency)}
                    </div>
                    <div className="text-sm text-gray-500">
                      {transaction.type}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(transaction.timestamp)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(transaction.status)}`}>
                      {getStatusIcon(transaction.status)}
                      {transaction.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(transaction.fraudProbability)}`}>
                        {(transaction.fraudProbability * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  {(user?.role === 'admin' || user?.role === 'analyst') && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setSelectedTransaction(transaction)}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        {transaction.isBlocked ? (
                          <button
                            onClick={() => handleUnblockTransaction(transaction.id)}
                            className="text-green-600 hover:text-green-900"
                            title="Débloquer"
                          >
                            <ShieldOff className="h-4 w-4" />
                          </button>
                        ) : (
                          <button
                            onClick={() => handleBlockTransaction(transaction.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Bloquer"
                          >
                            <Shield className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredTransactions.length === 0 && (
          <div className="text-center py-12">
            <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune transaction trouvée</h3>
            <p className="text-gray-500">Essayez de modifier vos filtres de recherche.</p>
          </div>
        )}
      </div>

      {/* Transaction Detail Modal */}
      {selectedTransaction && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Détails de la Transaction</h2>
                <button
                  onClick={() => setSelectedTransaction(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">ID Transaction</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedTransaction.id}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Montant</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {formatCurrency(selectedTransaction.amount, selectedTransaction.currency)}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Compte Source</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedTransaction.fromAccount}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Compte Destination</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedTransaction.toAccount}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Date</label>
                    <p className="mt-1 text-sm text-gray-900">{formatDate(selectedTransaction.timestamp)}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Type</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedTransaction.type}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Localisation</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedTransaction.location}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Appareil</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedTransaction.deviceInfo}</p>
                  </div>
                </div>

                <div className="border-t pt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Analyse de Risque</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Probabilité de Fraude</label>
                      <div className="mt-1 flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-red-500 h-2 rounded-full" 
                            style={{ width: `${selectedTransaction.fraudProbability * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {(selectedTransaction.fraudProbability * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Score de Risque</label>
                      <div className="mt-1 flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-yellow-500 h-2 rounded-full" 
                            style={{ width: `${selectedTransaction.riskScore * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {(selectedTransaction.riskScore * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {selectedTransaction.isBlocked && (
                  <div className="border-t pt-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Informations de Blocage</h3>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <p className="text-sm text-red-800">
                        <strong>Bloquée par :</strong> {selectedTransaction.blockedBy}
                      </p>
                      <p className="text-sm text-red-800 mt-1">
                        <strong>Date de blocage :</strong> {selectedTransaction.blockedAt && formatDate(selectedTransaction.blockedAt)}
                      </p>
                    </div>
                  </div>
                )}

                {(user?.role === 'admin' || user?.role === 'analyst') && (
                  <div className="border-t pt-6 flex gap-3">
                    {selectedTransaction.isBlocked ? (
                      <button
                        onClick={() => {
                          handleUnblockTransaction(selectedTransaction.id);
                          setSelectedTransaction(null);
                        }}
                        className="btn btn-primary flex items-center gap-2"
                      >
                        <ShieldOff className="h-4 w-4" />
                        Débloquer la Transaction
                      </button>
                    ) : (
                      <button
                        onClick={() => {
                          handleBlockTransaction(selectedTransaction.id);
                          setSelectedTransaction(null);
                        }}
                        className="btn btn-danger flex items-center gap-2"
                      >
                        <Shield className="h-4 w-4" />
                        Bloquer la Transaction
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Transactions;