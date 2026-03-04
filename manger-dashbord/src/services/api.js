import axios from 'axios';

const API_URL = process.env.REACT_APP_API_BASE_URL;

if (!API_URL) {
  throw new Error('REACT_APP_API_BASE_URL environment variable is required');
}

// Creating an axios instance with base URL
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
  }
});

// Add a request interceptor to add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    // Add cache-busting headers
    config.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
    config.headers['Pragma'] = 'no-cache';
    config.headers['Expires'] = '0';
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle token expiration
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is 401 and we haven't retried yet
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Redirect to login page
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      
      return Promise.reject(error);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
