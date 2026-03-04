import React, { createContext, useState, useContext, useEffect } from 'react';
import AuthService from '../services/auth.service';

// Create the auth context
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const initAuth = async () => {
      if (AuthService.isAuthenticated()) {
        setUser(AuthService.getCurrentUser());
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  // Login method
  const login = async (username, password) => {
    const result = await AuthService.login(username, password);
    if (result.success) {
      setUser(result.data);
      return { success: true };
    }
    return { success: false, message: result.message };
  };

  // Logout method
  const logout = () => {
    AuthService.logout();
    setUser(null);
  };

  // Check if user is manager
  const isManager = () => {
    return user && user.role === 'manager';
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    isManager
  };

  return (
    <AuthContext.Provider value={value}>
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
