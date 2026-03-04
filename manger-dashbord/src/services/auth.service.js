import { jwtDecode } from 'jwt-decode';
import apiClient from './api';

const AuthService = {
  login: async (username, password) => {
    try {
      // Create FormData object and append username and password
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      // Send as form-urlencoded data (required by OAuth2 in FastAPI)
      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      // Store token in localStorage
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        
        // Create user object with role and user_id from response
        const user = {
          user_id: response.data.user_id,
          role: response.data.role,
          username: username
        };
        localStorage.setItem('user', JSON.stringify(user));
        
        return { success: true, data: user };
      } else {
        return { success: false, message: 'No token received' };
      }
    } catch (error) {
      console.error("Login error:", error);
      return { 
        success: false, 
        message: error.response?.data?.detail || 'An error occurred during login'
      };
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  },
  
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    if (!token || !userStr) {
      return false;
    }
    
    try {
      const decoded = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      const user = JSON.parse(userStr);
      
      // Check if token is expired
      if (decoded.exp < currentTime) {
        // Token is expired, remove it
        AuthService.logout();
        return false;
      }
      
      // Check if user has manager role
      if (user.role !== 'manager') {
        return false;
      }
      
      return true;
    } catch (error) {
      console.error("Authentication error:", error);
      return false;
    }
  }
};

export default AuthService;
