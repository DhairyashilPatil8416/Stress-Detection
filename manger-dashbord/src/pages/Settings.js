import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const Settings = () => {
  const { user } = useAuth();
  const [apiUrl, setApiUrl] = useState(localStorage.getItem('apiUrl') || process.env.REACT_APP_API_BASE_URL || 'API URL not configured');
  const [refreshInterval, setRefreshInterval] = useState(localStorage.getItem('refreshInterval') || '30');
  const [darkMode, setDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [notification, setNotification] = useState(null);
  
  // Save settings
  const handleSave = () => {
    localStorage.setItem('apiUrl', apiUrl);
    localStorage.setItem('refreshInterval', refreshInterval);
    localStorage.setItem('darkMode', darkMode);
    
    setNotification({
      type: 'success',
      message: 'Settings saved successfully'
    });
    
    // Hide notification after 3 seconds
    setTimeout(() => {
      setNotification(null);
    }, 3000);
  };
  
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Configure your dashboard preferences
        </p>
      </div>
      
      {notification && (
        <div className={`mb-6 p-4 rounded-md ${notification.type === 'success' ? 'bg-green-50' : 'bg-red-50'}`}>
          <div className="flex">
            <div className="flex-shrink-0">
              {notification.type === 'success' ? (
                <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <div className="ml-3">
              <p className={`text-sm font-medium ${notification.type === 'success' ? 'text-green-800' : 'text-red-800'}`}>
                {notification.message}
              </p>
            </div>
          </div>
        </div>
      )}
      
      <div className="bg-white shadow rounded-lg">
        {/* User Information */}
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Account Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                type="text"
                name="username"
                id="username"
                disabled
                value={user?.username || ''}
                className="mt-1 block w-full bg-gray-100 border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight cursor-not-allowed"
              />
              <p className="mt-1 text-xs text-gray-500">Contact administrator to change username</p>
            </div>
            
            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700">
                Role
              </label>
              <input
                type="text"
                name="role"
                id="role"
                disabled
                value="Manager"
                className="mt-1 block w-full bg-gray-100 border border-gray-300 rounded-md py-2 px-3 text-gray-700 leading-tight cursor-not-allowed"
              />
            </div>
          </div>
        </div>
        
        {/* API Settings */}
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900 mb-4">API Settings</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="apiUrl" className="block text-sm font-medium text-gray-700">
                API URL
              </label>
              <input
                type="text"
                name="apiUrl"
                id="apiUrl"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md py-2 px-3 text-gray-700 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">URL of the StressSense backend API</p>
            </div>
            
            <div>
              <label htmlFor="refreshInterval" className="block text-sm font-medium text-gray-700">
                Default Refresh Interval (seconds)
              </label>
              <select
                name="refreshInterval"
                id="refreshInterval"
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md py-2 px-3 text-gray-700 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="10">10 seconds</option>
                <option value="30">30 seconds</option>
                <option value="60">1 minute</option>
                <option value="300">5 minutes</option>
              </select>
              <p className="mt-1 text-xs text-gray-500">How often data refreshes by default</p>
            </div>
          </div>
        </div>
        
        {/* Display Settings */}
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Display Settings</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="darkMode"
                  id="darkMode"
                  checked={darkMode}
                  onChange={(e) => setDarkMode(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="darkMode" className="ml-2 block text-sm font-medium text-gray-700">
                  Dark Mode (Coming Soon)
                </label>
              </div>
              <p className="mt-1 ml-6 text-xs text-gray-500">Enable dark mode for the dashboard</p>
            </div>
          </div>
        </div>
        
        {/* Save Button */}
        <div className="p-6 flex justify-end">
          <button
            type="button"
            onClick={handleSave}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
