import React from 'react';
import { AlertTriangle, Clock, User } from 'lucide-react';
import { FraudAlert } from '../../types';
import { formatDate } from '../../utils/formatters';

interface AlertsListProps {
  alerts: FraudAlert[];
  onAlertClick?: (alert: FraudAlert) => void;
}

const AlertsList: React.FC<AlertsListProps> = ({ alerts, onAlertClick }) => {
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

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Alertes Récentes
        </h3>
        <span className="text-sm text-gray-500">
          {alerts.length} alertes
        </span>
      </div>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {alerts.slice(0, 10).map((alert) => (
          <div
            key={alert.id}
            className={`p-4 rounded-lg border cursor-pointer hover:shadow-sm transition-shadow ${getSeverityColor(alert.severity)}`}
            onClick={() => onAlertClick?.(alert)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 mt-0.5" />
                <div>
                  <h4 className="font-medium text-sm">{alert.type}</h4>
                  <p className="text-xs opacity-80 mt-1">{alert.description}</p>
                  <div className="flex items-center gap-4 mt-2 text-xs opacity-70">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatDate(alert.timestamp)}
                    </div>
                    {alert.assignedTo && (
                      <div className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        {alert.assignedTo}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs font-medium">
                  {(alert.fraudProbability * 100).toFixed(1)}%
                </div>
                <div className="text-xs opacity-70 mt-1">
                  {alert.severity.toUpperCase()}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {alerts.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <AlertTriangle className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>Aucune alerte récente</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertsList;