import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import StressService from '../services/stress.service';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorDisplay from '../components/ErrorDisplay';

const Employees = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      console.log('Employees component - Starting to fetch employees');
      setLoading(true);
      const data = await StressService.getAllEmployees();
      console.log('Employees component - Fetched employees:', data);
      console.log('Employees component - Data type:', typeof data);
      console.log('Employees component - Is array?', Array.isArray(data));
      
      if (Array.isArray(data)) {
        setEmployees(data);
      } else if (data && typeof data === 'object') {
        // Handle case where response might be wrapped in another object
        const employeesArray = data.employees || data.data || [];
        console.log('Employees component - Extracted array:', employeesArray);
        setEmployees(employeesArray);
      } else {
        console.warn('Employees component - Unexpected data format:', data);
        setEmployees([]);
      }
      
      setError(null);
    } catch (err) {
      console.error('Employees component - Error fetching employees:', err);
      setError('Failed to load employees. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const filteredEmployees = employees.filter(employee => {
    const searchTerm = filter.toLowerCase();
    const name = employee.display_name || employee.name || '';
    const id = employee.employee_id || '';
    return name.toLowerCase().includes(searchTerm) || id.toLowerCase().includes(searchTerm);
  });

  return (
    <div className="px-4 py-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Employees</h1>
      
      {/* Search and filter */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            className="block w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            placeholder="Search employees..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorDisplay message={error} />
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <ul className="divide-y divide-gray-200">
            {filteredEmployees.length === 0 ? (
              <li className="px-6 py-4 text-center text-gray-500">
                {filter ? "No employees found matching your search." : "No employee data available."}
              </li>
            ) : (
              filteredEmployees.map((employee) => (
                <li key={employee.employee_id} className="px-4 py-4 hover:bg-gray-50">
                  <Link 
                    to={`/dashboard/employee/${employee.employee_id}`}
                    className="block"
                  >
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                          <span className="text-lg font-medium text-gray-600">
                            {(employee.display_name || employee.name || '?')[0].toUpperCase()}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-base font-medium text-gray-900">
                          {employee.display_name || employee.name || 'Unknown Employee'}
                        </div>
                        <div className="text-sm text-gray-500">
                          ID: {employee.employee_id || 'Unknown'}
                        </div>
                        {employee.department && (
                          <div className="text-sm text-gray-500">
                            Department: {employee.department}
                          </div>
                        )}
                      </div>
                    </div>
                  </Link>
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Employees;
