import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import './App.css';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import DashboardLayout from './components/DashboardLayout';

// Pages
import Login from './pages/Login';
import Overview from './pages/Overview';
import EmployeeDetail from './pages/EmployeeDetail';
import Employees from './pages/Employees';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected routes with dashboard layout */}
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              <Route path="/dashboard" element={<Overview />} />
              <Route path="/dashboard/employees" element={<Employees />} />
              <Route path="/dashboard/employee/:employeeId" element={<EmployeeDetail />} />
              <Route path="/dashboard/analytics" element={<Analytics />} />
              <Route path="/dashboard/settings" element={<Settings />} />
            </Route>
          </Route>
          
          {/* Default redirect */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
