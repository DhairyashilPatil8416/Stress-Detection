import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { useAuth } from '../contexts/AuthContext';

const DashboardLayout = () => {
  const { user } = useAuth();

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Topbar */}
        <header className="bg-white shadow">
          <div className="px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
            <h1 className="text-lg font-semibold text-gray-900">Dashboard</h1>
            <div className="flex items-center">
              <span className="text-sm text-gray-500 mr-2">Welcome, {user?.username || 'Manager'}</span>
            </div>
          </div>
        </header>
        
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
