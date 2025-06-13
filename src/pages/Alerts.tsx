import React, { useState } from 'react';
import { 
  AlertTriangle, 
  Clock, 
  User, 
  Eye, 
  CheckCircle, 
  XCircle,
  Filter,
  Search
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useRealTimeData } from '../hooks/useRealTimeData';
import { FraudAlert } from '../types';
import { formatDate } from '../utils/formatters';

const Alerts: React.FC = () => {
  const { user } = useAuth();
  const { alerts, transactions, loading, updateAlert } = useRealTimeData();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [selectedAlert, setSelectedAlert] = useState<FraudAlert | null>(null);

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = 
      alert.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || alert.status === statusFilter;
    const matchesSeverity = severityFilter === 'all' || alert.severity === severityFilter;

    return matchesSearch && matchesStatus && matchesSeverity;
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'high':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'text-red-600 bg-red-50';
      case 'investigating':
        return 'text-yellow-600 bg-yellow-50';
      case 'resolved':
        return 'text-green-600 bg-green-50';
      case 'false_positive':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const handleUpdateStatus = async (alertId: string, status: string) => {
    await updateAlert(alertId, status, user?.name);
  };

  const findTransactionForAlert = (alert: FraudAlert) => {
    return transactions.find(tx => tx.id === alert.transactionId);
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
          <h1 className="text-2xl font-bold text-gray-900">Alertes de Fraude</h1>
          <p className="text-gray-600 mt-1">
            Surveillance et gestion des alertes IA
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 bg-red-50 text-red-700 rounded-lg">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-sm font-medium">
            {alerts.filter(a => a.status === 'open').length} alertes ouvertes
          </span>
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
                placeholder="Rechercher dans les alertes..."
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
            <option value="open">Ouvert</option>
            <option value="investigating">En cours</option>
            <option value="resolved">Résolu</option>
            <option value="false_positive">Faux positif</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="input w-auto"
          >
            <option value="all">Toutes les sévérités</option>
            <option value="critical">Critique</option>
            <option value="high">Élevée</option>
            <option value="medium">Moyenne</option>
            <option value="low">Faible</option>
          </select>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.map((alert) => {
          const transaction = findTransactionForAlert(alert);
          
          return (
            <div
              key={alert.id}
              className={`card p-6 border-l-4 ${getSeverityColor(alert.severity).includes('red') ? 'border-l-red-500' : 
                getSeverityColor(alert.severity).includes('orange') ? 'border-l-orange-500' :
                getSeverityColor(alert.severity).includes('yellow') ? 'border-l-yellow-500' : 'border-l-blue-500'}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <AlertTriangle className={`h-5 w-5 ${
                      alert.severity === 'critical' ? 'text-red-600' :
                      alert.severity === 'high' ? 'text-orange-600' :
                      alert.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                    }`} />
                    <h3 className="text-lg font-semibold text-gray-900">{alert.type}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(alert.status)}`}>
                      {alert.status}
                    </span>
                  </div>
                  
                  <p className="text-gray-700 mb-4">{alert.description}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-500 uppercase">Probabilité de Fraude</label>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-red-500 h-2 rounded-full" 
                            style={{ width: `${alert.fraudProbability * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {(alert.fraudProbability * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-xs font-medium text-gray-500 uppercase">Confiance IA</label>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ width: `${alert.aiConfidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {(alert.aiConfidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-xs font-medium text-gray-500 uppercase">Action Recommandée</label>
                      <span className={`inline-block mt-1 px-2 py-1 rounded text-xs font-medium ${
                        alert.recommendedAction === 'block' ? 'bg-red-100 text-red-800' :
                        alert.recommendedAction === 'investigate' ? 'bg-yellow-100 text-yellow-800' :
                        alert.recommendedAction === 'review' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {alert.recommendedAction}
                      </span>
                    </div>
                  </div>

                  {transaction && (
                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <h4 className="font-medium text-gray-900 mb-2">Transaction Associée</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">ID:</span>
                          <span className="ml-2 font-medium">{transaction.id}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Montant:</span>
                          <span className="ml-2 font-medium">{transaction.amount.toFixed(2)} {transaction.currency}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">De:</span>
                          <span className="ml-2 font-medium">{transaction.fromAccount}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Vers:</span>
                          <span className="ml-2 font-medium">{transaction.toAccount}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {formatDate(alert.timestamp)}
                    </div>
                    {alert.assignedTo && (
                      <div className="flex items-center gap-1">
                        <User className="h-4 w-4" />
                        Assigné à {alert.assignedTo}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex flex-col gap-2 ml-4">
                  <button
                    onClick={() => setSelectedAlert(alert)}
                    className="btn btn-secondary p-2"
                    title="Voir les détails"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  
                  {alert.status === 'open' && (
                    <button
                      onClick={() => handleUpdateStatus(alert.id, 'investigating')}
                      className="btn btn-primary p-2"
                      title="Commencer l'investigation"
                    >
                      <Clock className="h-4 w-4" />
                    </button>
                  )}
                  
                  {alert.status === 'investigating' && (
                    <>
                      <button
                        onClick={() => handleUpdateStatus(alert.id, 'resolved')}
                        className="btn p-2 bg-green-600 text-white hover:bg-green-700"
                        title="Marquer comme résolu"
                      >
                        <CheckCircle className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleUpdateStatus(alert.id, 'false_positive')}
                        className="btn btn-secondary p-2"
                        title="Marquer comme faux positif"
                      >
                        <XCircle className="h-4 w-4" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {filteredAlerts.length === 0 && (
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune alerte trouvée</h3>
            <p className="text-gray-500">Essayez de modifier vos filtres de recherche.</p>
          </div>
        )}
      </div>

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Détails de l'Alerte</h2>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Alert Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">ID Alerte</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedAlert.id}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Type</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedAlert.type}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Sévérité</label>
                    <span className={`inline-block mt-1 px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(selectedAlert.severity)}`}>
                      {selectedAlert.severity.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Statut</label>
                    <span className={`inline-block mt-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedAlert.status)}`}>
                      {selectedAlert.status}
                    </span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedAlert.description}</p>
                </div>

                {/* AI Analysis */}
                <div className="border-t pt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Analyse IA</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Probabilité de Fraude</label>
                      <div className="mt-2 flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-3">
                          <div 
                            className="bg-red-500 h-3 rounded-full" 
                            style={{ width: `${selectedAlert.fraudProbability * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {(selectedAlert.fraudProbability * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Confiance IA</label>
                      <div className="mt-2 flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-3">
                          <div 
                            className="bg-blue-500 h-3 rounded-full" 
                            style={{ width: `${selectedAlert.aiConfidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {(selectedAlert.aiConfidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Action Recommandée</label>
                      <span className={`inline-block mt-2 px-3 py-1 rounded text-sm font-medium ${
                        selectedAlert.recommendedAction === 'block' ? 'bg-red-100 text-red-800' :
                        selectedAlert.recommendedAction === 'investigate' ? 'bg-yellow-100 text-yellow-800' :
                        selectedAlert.recommendedAction === 'review' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {selectedAlert.recommendedAction}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="border-t pt-6 flex gap-3">
                  {selectedAlert.status === 'open' && (
                    <button
                      onClick={() => {
                        handleUpdateStatus(selectedAlert.id, 'investigating');
                        setSelectedAlert(null);
                      }}
                      className="btn btn-primary"
                    >
                      Commencer l'Investigation
                    </button>
                  )}
                  
                  {selectedAlert.status === 'investigating' && (
                    <>
                      <button
                        onClick={() => {
                          handleUpdateStatus(selectedAlert.id, 'resolved');
                          setSelectedAlert(null);
                        }}
                        className="btn bg-green-600 text-white hover:bg-green-700"
                      >
                        Marquer comme Résolu
                      </button>
                      <button
                        onClick={() => {
                          handleUpdateStatus(selectedAlert.id, 'false_positive');
                          setSelectedAlert(null);
                        }}
                        className="btn btn-secondary"
                      >
                        Faux Positif
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;