import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Sidebar = () => {
  const location = useLocation();
  const { user, logout } = useAuth();
  
  // Navigation items
  const navItems = [
    { name: 'Overview', path: '/dashboard', icon: 'grid' },
    { name: 'Employees', path: '/dashboard/employees', icon: 'users' },
    { name: 'Analytics', path: '/dashboard/analytics', icon: 'bar-chart-2' },
    { name: 'Settings', path: '/dashboard/settings', icon: 'settings' },
  ];
  
  // Check if the current path matches the nav item path
  const isActive = (path) => {
    return location.pathname === path;
  };
  
  return (
    <div className="bg-gray-800 text-white w-64 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-4">
        <h1 className="text-xl font-bold">StressSense</h1>
        <p className="text-sm text-gray-400">Manager Dashboard</p>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 px-2 py-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.name}>
              <Link
                to={item.path}
                className={`flex items-center px-4 py-2 text-sm rounded-md ${
                  isActive(item.path)
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <span className="mr-3">
                  <i data-feather={item.icon}></i>
                </span>
                {item.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      
      {/* User Profile */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center">
          <div className="w-10 h-10 rounded-full bg-gray-600 flex items-center justify-center">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium">{user?.username || 'User'}</p>
            <p className="text-xs text-gray-400">Manager</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="mt-4 w-full flex items-center px-4 py-2 text-sm text-gray-300 rounded-md hover:bg-gray-700"
        >
          <span className="mr-3">
            <i data-feather="log-out"></i>
          </span>
          Sign Out
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
