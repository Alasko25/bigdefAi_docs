import React, { useState } from 'react';
import { Play, Square, Settings, BarChart3, Zap } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { SimulationConfig } from '../types';
import { simulationAPI } from '../services/api';

const Simulation: React.FC = () => {
  const { user } = useAuth();
  const [isRunning, setIsRunning] = useState(false);
  const [config, setConfig] = useState<SimulationConfig>({
    transactionCount: 100,
    fraudRate: 0.05,
    bankId: user?.bankId || 'bnp',
    timeRange: 'realtime',
    transactionTypes: ['transfer', 'payment', 'withdrawal'],
    amountRange: { min: 100, max: 50000 },
  });
  const [currentSimulationId, setCurrentSimulationId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const handleStartSimulation = async () => {
    try {
      setIsRunning(true);
      const response = await simulationAPI.startSimulation(config);
      setCurrentSimulationId(response.simulationId);
      
      // Mock progress updates for demo
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsRunning(false);
            return 100;
          }
          return prev + 10;
        });
      }, 1000);
    } catch (error) {
      console.error('Failed to start simulation:', error);
      // For demo, simulate locally
      setIsRunning(true);
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsRunning(false);
            return 100;
          }
          return prev + 10;
        });
      }, 1000);
    }
  };

  const handleStopSimulation = async () => {
    if (currentSimulationId) {
      try {
        await simulationAPI.stopSimulation(currentSimulationId);
      } catch (error) {
        console.error('Failed to stop simulation:', error);
      }
    }
    setIsRunning(false);
    setProgress(0);
    setCurrentSimulationId(null);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Simulation de Transactions</h1>
          <p className="text-gray-600 mt-1">
            Générez des transactions virtuelles pour tester le système de détection
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 text-blue-700 rounded-lg">
          <Zap className="h-4 w-4" />
          <span className="text-sm font-medium">Mode Simulation</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card p-6">
            <div className="flex items-center gap-2 mb-6">
              <Settings className="h-5 w-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Configuration</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre de Transactions
                </label>
                <input
                  type="number"
                  value={config.transactionCount}
                  onChange={(e) => setConfig(prev => ({ ...prev, transactionCount: parseInt(e.target.value) }))}
                  className="input w-full"
                  min="1"
                  max="10000"
                  disabled={isRunning}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Taux de Fraude (%)
                </label>
                <input
                  type="number"
                  value={config.fraudRate * 100}
                  onChange={(e) => setConfig(prev => ({ ...prev, fraudRate: parseFloat(e.target.value) / 100 }))}
                  className="input w-full"
                  min="0"
                  max="50"
                  step="0.1"
                  disabled={isRunning}
                />
              </div>

              {user?.role === 'admin' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Banque Cible
                  </label>
                  <select
                    value={config.bankId}
                    onChange={(e) => setConfig(prev => ({ ...prev, bankId: e.target.value }))}
                    className="input w-full"
                    disabled={isRunning}
                  >
                    <option value="bnp">BNP Paribas</option>
                    <option value="sg">Société Générale</option>
                    <option value="ca">Crédit Agricole</option>
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Intervalle de Temps
                </label>
                <select
                  value={config.timeRange}
                  onChange={(e) => setConfig(prev => ({ ...prev, timeRange: e.target.value as any }))}
                  className="input w-full"
                  disabled={isRunning}
                >
                  <option value="realtime">Temps réel</option>
                  <option value="1hour">1 heure</option>
                  <option value="1day">1 jour</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Montant Minimum (€)
                </label>
                <input
                  type="number"
                  value={config.amountRange.min}
                  onChange={(e) => setConfig(prev => ({ 
                    ...prev, 
                    amountRange: { ...prev.amountRange, min: parseInt(e.target.value) }
                  }))}
                  className="input w-full"
                  min="1"
                  disabled={isRunning}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Montant Maximum (€)
                </label>
                <input
                  type="number"
                  value={config.amountRange.max}
                  onChange={(e) => setConfig(prev => ({ 
                    ...prev, 
                    amountRange: { ...prev.amountRange, max: parseInt(e.target.value) }
                  }))}
                  className="input w-full"
                  min="100"
                  disabled={isRunning}
                />
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Types de Transactions
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {['transfer', 'payment', 'withdrawal', 'deposit'].map(type => (
                  <label key={type} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={config.transactionTypes.includes(type)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setConfig(prev => ({ 
                            ...prev, 
                            transactionTypes: [...prev.transactionTypes, type]
                          }));
                        } else {
                          setConfig(prev => ({ 
                            ...prev, 
                            transactionTypes: prev.transactionTypes.filter(t => t !== type)
                          }));
                        }
                      }}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      disabled={isRunning}
                    />
                    <span className="text-sm text-gray-700 capitalize">{type}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Control Panel */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Contrôles</h2>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                isRunning ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {isRunning ? 'En cours' : 'Arrêté'}
              </div>
            </div>

            {isRunning && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Progression</span>
                  <span className="text-sm text-gray-600">{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300" 
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
              </div>
            )}

            <div className="flex gap-3">
              {!isRunning ? (
                <button
                  onClick={handleStartSimulation}
                  className="btn btn-primary flex items-center gap-2"
                  disabled={config.transactionTypes.length === 0}
                >
                  <Play className="h-4 w-4" />
                  Démarrer la Simulation
                </button>
              ) : (
                <button
                  onClick={handleStopSimulation}
                  className="btn btn-danger flex items-center gap-2"
                >
                  <Square className="h-4 w-4" />
                  Arrêter la Simulation
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Statistics Panel */}
        <div className="space-y-6">
          <div className="card p-6">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="h-5 w-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Statistiques</h2>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Transactions générées</span>
                <span className="font-medium">{Math.floor(progress * config.transactionCount / 100)}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Fraudes simulées</span>
                <span className="font-medium text-red-600">
                  {Math.floor(progress * config.transactionCount * config.fraudRate / 100)}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Taux de détection</span>
                <span className="font-medium text-green-600">94.2%</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Faux positifs</span>
                <span className="font-medium text-yellow-600">2.1%</span>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Paramètres Actuels</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Transactions:</span>
                <span className="font-medium">{config.transactionCount.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Taux de fraude:</span>
                <span className="font-medium">{(config.fraudRate * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Montant:</span>
                <span className="font-medium">
                  {config.amountRange.min}€ - {config.amountRange.max.toLocaleString()}€
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Types:</span>
                <span className="font-medium">{config.transactionTypes.length}</span>
              </div>
            </div>
          </div>

          <div className="card p-6 bg-gradient-to-r from-blue-50 to-primary-50 border-primary-200">
            <h3 className="font-semibold text-primary-900 mb-2">💡 Conseil</h3>
            <p className="text-sm text-primary-800">
              Utilisez un taux de fraude réaliste (2-5%) pour des tests représentatifs. 
              Les simulations aident à valider les performances du modèle IA.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Simulation;