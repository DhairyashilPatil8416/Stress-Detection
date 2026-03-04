import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import StressService from '../services/stress.service';

const StressLevelBadge = ({ level }) => {
  const badgeClasses = {
    'Low': 'bg-green-100 text-green-800',
    'Medium': 'bg-yellow-100 text-yellow-800',
    'High': 'bg-red-100 text-red-800'
  };
  
  const badgeIcons = {
    'Low': '🟢',
    'Medium': '🟠',
    'High': '🔴'
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badgeClasses[level] || 'bg-gray-100'}`}>
      {badgeIcons[level]} {level}
    </span>
  );
};

const Overview = () => {
  const [employeeData, setEmployeeData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');
  const [refreshInterval, setRefreshInterval] = useState(30); // in seconds
  
  const fetchEmployeeData = useCallback(async () => {
    setLoading(true);
    
    try {
      const result = await StressService.getLatestStressData();
      
      if (result.success) {
        // Force a new array reference to ensure React detects the change
        setEmployeeData([...result.data]);
        console.log('Employee data received:', result.data);
        console.log('First employee department:', result.data[0]?.department);
        setError(null);
      } else {
        setError('Failed to fetch employee data');
      }
    } catch (err) {
      setError('An unexpected error occurred');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);
  
  useEffect(() => {
    fetchEmployeeData();
    
    // Set up auto refresh
    const intervalId = setInterval(fetchEmployeeData, refreshInterval * 1000);
    
    return () => clearInterval(intervalId);
  }, [refreshInterval, fetchEmployeeData]);
  
  // Filter employees based on search term
  const filteredEmployees = employeeData.filter(employee => {
    const searchTerm = filter.toLowerCase();
    return (
      (employee.display_name || employee.name || '')?.toLowerCase().includes(searchTerm) ||
      employee.department?.toLowerCase().includes(searchTerm) ||
      employee.employee_id?.toLowerCase().includes(searchTerm)
    );
  });
  
  // Handle refresh interval change
  const handleIntervalChange = (e) => {
    const value = parseInt(e.target.value);
    setRefreshInterval(value);
  };
  
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Employee Stress Overview</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor real-time stress levels across your team
        </p>
      </div>
      
      {/* Controls */}
      <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
        <div className="relative rounded-md shadow-sm w-full sm:w-64">
          <input
            type="text"
            placeholder="Search employees..."
            className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-3 pr-10 py-2 sm:text-sm border-gray-300 rounded-md"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
            </svg>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">
            Auto-refresh:
          </label>
          <select
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            value={refreshInterval}
            onChange={handleIntervalChange}
          >
            <option value="10">Every 10s</option>
            <option value="30">Every 30s</option>
            <option value="60">Every 1m</option>
            <option value="300">Every 5m</option>
          </select>
          
          <button
            onClick={fetchEmployeeData}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg className="mr-1 -ml-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>
      
      {/* Employee Table */}
      {loading && employeeData.length === 0 ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 p-4 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                {error}
              </h3>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col">
          <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
              <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Employee
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Department
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Stress Level
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Emotion
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Confidence
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Updated
                      </th>
                      <th scope="col" className="relative px-6 py-3">
                        <span className="sr-only">Actions</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredEmployees.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="px-6 py-4 text-center text-sm text-gray-500">
                          {filter ? "No employees found matching your search." : "No employee data available."}
                        </td>
                      </tr>
                    ) : (
                      filteredEmployees.map((employee) => {
                        console.log('Rendering employee:', employee.employee_id, 'Department:', employee.department);
                        return (
                        <tr key={`${employee.employee_id}-${employee.timestamp || Date.now()}`} className={employee.stress_level === 'High' ? 'bg-red-50' : ''}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="flex-shrink-0 h-10 w-10">
                                <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600">
                                  {(employee.display_name || employee.name)?.charAt(0).toUpperCase() || 'E'}
                                </div>
                              </div>
                              <div className="ml-4">
                                <div className="text-sm font-medium text-gray-900">
                                  {employee.display_name || employee.name || employee.employee_id}
                                </div>
                                <div className="text-sm text-gray-500">
                                  {employee.employee_id}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{employee.department || 'N/A'}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <StressLevelBadge level={employee.latest_stress_level || employee.stress_level} />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {employee.latest_emotion || employee.emotion}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">
                              {Math.round(employee.confidence || 0)}%
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(employee.timestamp).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <Link 
                              to={`/dashboard/employee/${employee.employee_id}`}
                              className="text-blue-600 hover:text-blue-900"
                            >
                              Details
                            </Link>
                          </td>
                        </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Overview;
