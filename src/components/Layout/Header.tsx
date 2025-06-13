import React from 'react';
import { Bell, Wifi, WifiOff, User, LogOut, Settings } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useRealTimeData } from '../../hooks/useRealTimeData';
import Logo from '../Logo';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { alerts, isConnected } = useRealTimeData();

  const activeAlerts = alerts.filter(a => a.status === 'open' || a.status === 'investigating').length;

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Logo className="h-8 w-8" />
          <div>
            <h1 className="text-lg font-semibold text-gray-900">
              Bienvenue, {user?.name}
            </h1>
            <p className="text-sm text-gray-500">
              {user?.role === 'admin' ? 'Administrateur Système' : 
               user?.role === 'analyst' ? `Analyste - ${user.bankName}` :
               `Client - ${user.bankName}`}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Connection Status */}
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
            isConnected 
              ? 'bg-gradient-to-r from-green-50 to-blue-50 border-green-200' 
              : 'bg-gradient-to-r from-red-50 to-orange-50 border-red-200'
          }`}>
            {isConnected ? (
              <>
                <Wifi className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-700">Temps Réel</span>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              </>
            ) : (
              <>
                <WifiOff className="h-4 w-4 text-red-600" />
                <span className="text-sm font-medium text-red-700">Hors Ligne</span>
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              </>
            )}
          </div>

          {/* Notifications */}
          {(user?.role === 'admin' || user?.role === 'analyst') && (
            <div className="relative">
              <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                <Bell className="h-5 w-5" />
                {activeAlerts > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {activeAlerts > 9 ? '9+' : activeAlerts}
                  </span>
                )}
              </button>
            </div>
          )}

          {/* User Menu */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg">
              <User className="h-4 w-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">{user?.name}</span>
            </div>
            
            {user?.role === 'admin' && (
              <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                <Settings className="h-5 w-5" />
              </button>
            )}
            
            <button 
              onClick={logout}
              className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;