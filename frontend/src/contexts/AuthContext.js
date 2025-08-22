import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  // Configure axios defaults
  useEffect(() => {
    // Set up axios to include credentials (cookies) with requests
    axios.defaults.withCredentials = true;
  }, []);

  // Check authentication status on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      // User not authenticated
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async (googleToken) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/auth/google`, {
        token: googleToken
      });
      
      setUser(response.data.user);
      setIsAuthenticated(true);
      
      return { success: true, user: response.data.user };
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    loginWithGoogle,
    logout,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};