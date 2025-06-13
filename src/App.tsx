import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Alerts from './pages/Alerts';
import Simulation from './pages/Simulation';

const AppRoutes: React.FC = () => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<Navigate to="/dashboard" />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<Dashboard />} />
        
        {/* Admin routes */}
        {user?.role === 'admin' && (
          <>
            <Route path="alerts" element={<Alerts />} />
            <Route path="transactions" element={<Transactions />} />
            <Route path="simulation" element={<Simulation />} />
          </>
        )}
        
        {/* Analyst routes */}
        {user?.role === 'analyst' && (
          <>
            <Route path="alerts" element={<Alerts />} />
            <Route path="transactions" element={<Transactions />} />
            <Route path="simulation" element={<Simulation />} />
          </>
        )}
        
        {/* Client routes */}
        {user?.role === 'client' && (
          <Route path="my-transactions" element={<Transactions />} />
        )}
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;