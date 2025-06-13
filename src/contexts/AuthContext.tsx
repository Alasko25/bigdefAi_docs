import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
import { authAPI } from '../services/api';
import { mockUsers } from '../services/mockData';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          // Try to get current user from API
          const currentUser = await authAPI.getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          // Fallback to mock data for demo
          console.log('Using mock authentication');
          const mockUser = mockUsers.find(u => u.email === localStorage.getItem('mock_user_email'));
          if (mockUser) {
            setUser(mockUser);
          } else {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('mock_user_email');
          }
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      // Try real API login first
      const response = await authAPI.login(email, password);
      localStorage.setItem('auth_token', response.access_token);
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      // Fallback to mock authentication for demo
      console.log('Using mock authentication');
      const mockUser = mockUsers.find(u => u.email === email);
      if (mockUser && password === 'demo123') {
        localStorage.setItem('auth_token', `mock_token_${mockUser.id}`);
        localStorage.setItem('mock_user_email', email);
        setUser(mockUser);
      } else {
        throw new Error('Invalid credentials');
      }
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('mock_user_email');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      isAuthenticated: !!user,
      loading,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};