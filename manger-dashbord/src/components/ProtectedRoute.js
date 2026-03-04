import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = () => {
  const { isAuthenticated, isManager, loading } = useAuth();
  const location = useLocation();

  // Show loading indicator if still checking authentication
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // If not authenticated or not a manager, redirect to login
  if (!isAuthenticated || !isManager()) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If authenticated and is a manager, render the child routes
  return <Outlet />;
};

export default ProtectedRoute;
