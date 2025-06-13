import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  AlertTriangle, 
  CreditCard, 
  Users, 
  BarChart3, 
  Settings,
  Play,
  Brain
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar: React.FC = () => {
  const { user } = useAuth();

  const getNavigationItems = () => {
    const baseItems = [
      { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    ];

    switch (user?.role) {
      case 'admin':
        return [
          ...baseItems,
          { to: '/alerts', icon: AlertTriangle, label: 'Alertes IA' },
          { to: '/transactions', icon: CreditCard, label: 'Transactions' },
          { to: '/banks', icon: BarChart3, label: 'Banques' },
          { to: '/users', icon: Users, label: 'Utilisateurs' },
          { to: '/ai-model', icon: Brain, label: 'Modèle IA' },
          { to: '/simulation', icon: Play, label: 'Simulation' },
          { to: '/settings', icon: Settings, label: 'Paramètres' },
        ];
      case 'analyst':
        return [
          ...baseItems,
          { to: '/alerts', icon: AlertTriangle, label: 'Alertes IA' },
          { to: '/transactions', icon: CreditCard, label: 'Transactions' },
          { to: '/analytics', icon: BarChart3, label: 'Analyses' },
          { to: '/simulation', icon: Play, label: 'Simulation' },
        ];
      case 'client':
        return [
          ...baseItems,
          { to: '/my-transactions', icon: CreditCard, label: 'Mes Transactions' },
        ];
      default:
        return baseItems;
    }
  };

  const navigationItems = getNavigationItems();

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-full flex flex-col">
      <div className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8">
            <svg viewBox="0 0 100 100" className="w-full h-full">
              <path
                d="M50 5 L85 20 L85 45 Q85 70 50 95 Q15 70 15 45 L15 20 Z"
                fill="none"
                stroke="#14b8a6"
                strokeWidth="3"
              />
              <g fill="none" stroke="#14b8a6" strokeWidth="2" strokeLinecap="round">
                <line x1="50" y1="25" x2="50" y2="75" />
                <circle cx="35" cy="35" r="3" fill="#14b8a6" />
                <circle cx="65" cy="35" r="3" fill="#14b8a6" />
                <circle cx="30" cy="50" r="3" fill="#14b8a6" />
                <circle cx="70" cy="50" r="3" fill="#14b8a6" />
                <circle cx="35" cy="65" r="3" fill="#14b8a6" />
                <circle cx="65" cy="65" r="3" fill="#14b8a6" />
                <line x1="35" y1="35" x2="45" y2="35" />
                <line x1="55" y1="35" x2="65" y2="35" />
                <line x1="30" y1="50" x2="45" y2="50" />
                <line x1="55" y1="50" x2="70" y2="50" />
                <line x1="35" y1="65" x2="45" y2="65" />
                <line x1="55" y1="65" x2="65" y2="65" />
                <line x1="35" y1="35" x2="35" y2="40" />
                <line x1="65" y1="35" x2="65" y2="40" />
                <line x1="35" y1="60" x2="35" y2="65" />
                <line x1="65" y1="60" x2="65" y2="65" />
              </g>
            </svg>
          </div>
          <div>
            <div className="text-lg font-bold text-gray-800">BIG DEFEND</div>
            <div className="text-sm font-medium text-primary-600">AI</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-4 space-y-2">
        {navigationItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700 border border-primary-200'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-2 px-3 py-2 bg-green-50 rounded-lg">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium text-green-700">IA Active</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;