import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import StressService from '../services/stress.service';

// Map stress level to numeric value for charting
const stressLevelToNumber = (level) => {
  switch(level) {
    case 'Low': return 1;
    case 'Medium': return 2;
    case 'High': return 3;
    default: return 0;
  }
};

// Format date for X-axis
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
};

// Group stress data by day for bar chart
const groupByDay = (data) => {
  const grouped = data.reduce((acc, item) => {
    const date = new Date(item.timestamp);
    const day = `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
    
    if (!acc[day]) {
      acc[day] = {
        day,
        date: new Date(day),
        totalStress: 0,
        count: 0
      };
    }
    
    acc[day].totalStress += stressLevelToNumber(item.stress_level);
    acc[day].count += 1;
    
    return acc;
  }, {});
  
  return Object.values(grouped)
    .map(item => ({
      ...item,
      avgStress: item.totalStress / item.count
    }))
    .sort((a, b) => a.date - b.date);
};

// Stress level badge component
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

const EmployeeDetail = () => {
  const { employeeId } = useParams();
  const navigate = useNavigate();
  
  const [employee, setEmployee] = useState(null);
  const [stressHistory, setStressHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisAttempted, setAnalysisAttempted] = useState(false);
  const [noStressData, setNoStressData] = useState(false);
  
  // Log current state for debugging
  useEffect(() => {
    console.log('Current employee data:', employee);
    console.log('Current stress history:', stressHistory);
  }, [employee, stressHistory]);

  // Prepare data for charts
  const lineChartData = stressHistory.map(entry => ({
    timestamp: formatDate(entry.timestamp),
    value: stressLevelToNumber(entry.stress_level),
    stress_level: entry.stress_level,
    emotion: entry.emotion,
    confidence: entry.confidence
  }));
  
  const barChartData = groupByDay(stressHistory);
  
  // Get latest stress reading
  const latestStress = stressHistory.length > 0 ? stressHistory[0] : null;
  
  // Fetch employee stress history
  const fetchEmployeeData = useCallback(async () => {
    setLoading(true);
    
    try {
      // First get employee details
      const employeeResult = await StressService.getEmployeeDetails(employeeId);
      console.log('Employee API Response:', employeeResult);
      
      if (employeeResult.success) {
        setEmployee(employeeResult.data || {});
      } else {
        console.error('Failed to fetch employee details:', employeeResult.message);
      }
      
      // Then get stress history
      const historyResult = await StressService.getEmployeeStressHistory(employeeId);
      console.log('Stress History API Response:', historyResult);
      
      if (historyResult.success) {
        setStressHistory(historyResult.data || []);
        setError(null);
      } else {
        setError('Failed to fetch employee data');
        console.error('Failed to fetch stress history:', historyResult.message);
      }
    } catch (err) {
      setError('An unexpected error occurred');
      console.error('Error fetching employee data:', err);
    } finally {
      setLoading(false);
    }
  }, [employeeId]);
  
  // Trigger a new stress analysis
  const handleAnalyzeNow = async () => {
    if (analyzing) return;
    
    setAnalyzing(true);
    setAnalysisAttempted(true);
    setNoStressData(false);
    setError(null);
    
    try {
      const result = await StressService.triggerStressAnalysis(employeeId);
      
      if (result.success) {
        // Wait a bit and then refresh data
        setTimeout(async () => {
          try {
            // Refresh stress history
            const historyResult = await StressService.getEmployeeStressHistory(employeeId);
            
            if (historyResult.success && historyResult.data && historyResult.data.length > 0) {
              setStressHistory(historyResult.data);
              setNoStressData(false);
            } else {
              setNoStressData(true);
            }
          } catch (refreshErr) {
            console.error('Error refreshing data:', refreshErr);
            setNoStressData(true);
          } finally {
            setAnalyzing(false);
          }
        }, 3000); // Reduced wait time for better UX
      } else {
        setError('Failed to trigger stress analysis');
        setAnalyzing(false);
      }
    } catch (err) {
      setError('An unexpected error occurred');
      console.error(err);
      setAnalyzing(false);
    }
  };
  
  useEffect(() => {
    fetchEmployeeData();
  }, [employeeId, fetchEmployeeData]);
  
  return (
    <div>
      {/* Header with back button */}
      <div className="mb-6 flex items-center">
        <button
          onClick={() => navigate(-1)}
          className="mr-4 p-2 rounded-full hover:bg-gray-200"
        >
          <svg className="h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {employee?.display_name || 'Employee'} - Stress Analysis
          </h1>
          <p className="text-sm text-gray-500">
            {employee?.department ? `${employee.department} Department` : ''}
            {employee?.employee_id ? ` · ID: ${employee.employee_id}` : ''}
          </p>
        </div>
      </div>
      
      {/* Content */}
      {loading && stressHistory.length === 0 ? (
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Latest Stress Card */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Latest Stress Reading</h2>
            
            {latestStress ? (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <StressLevelBadge level={latestStress.stress_level} />
                  <span className="text-sm text-gray-500">
                    {new Date(latestStress.timestamp).toLocaleString()}
                  </span>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Emotion:</span>
                    <span className="ml-2 text-sm text-gray-900">{latestStress.emotion}</span>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Confidence:</span>
                    <span className="ml-2 text-sm text-gray-900">{Math.round(latestStress.confidence || 0)}%</span>
                  </div>
                </div>
                
                <button
                  onClick={handleAnalyzeNow}
                  disabled={analyzing}
                  className={`mt-6 w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${analyzing ? 'opacity-70 cursor-not-allowed' : ''}`}
                >
                  {analyzing ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing...
                    </>
                  ) : (
                    'Analyze Now'
                  )}
                </button>
              </div>
            ) : analysisAttempted && noStressData ? (
              <div className="text-center py-8">
                <div className="text-sm text-gray-500 mb-4">
                  Stress is not found at this time. Try again.
                </div>
                <button
                  onClick={handleAnalyzeNow}
                  disabled={analyzing}
                  className={`inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${analyzing ? 'opacity-70 cursor-not-allowed' : ''}`}
                >
                  {analyzing ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing...
                    </>
                  ) : (
                    'Try Again'
                  )}
                </button>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-sm text-gray-500 mb-4">No stress readings available</div>
                <button
                  onClick={handleAnalyzeNow}
                  disabled={analyzing}
                  className={`inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${analyzing ? 'opacity-70 cursor-not-allowed' : ''}`}
                >
                  {analyzing ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing...
                    </>
                  ) : (
                    'Analyze Now'
                  )}
                </button>
              </div>
            )}
          </div>
          
          {/* Line Chart */}
          <div className="bg-white shadow rounded-lg p-6 lg:col-span-2">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Stress Level Over Time</h2>
            
            {lineChartData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={lineChartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis domain={[0, 4]} ticks={[1, 2, 3]} tickFormatter={(value) => {
                      switch(value) {
                        case 1: return 'Low';
                        case 2: return 'Medium';
                        case 3: return 'High';
                        default: return '';
                      }
                    }} />
                    <Tooltip 
                      formatter={(value, name) => {
                        switch(value) {
                          case 1: return 'Low';
                          case 2: return 'Medium';
                          case 3: return 'High';
                          default: return value;
                        }
                      }}
                      labelFormatter={(label) => `Time: ${label}`}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="value" name="Stress Level" stroke="#3B82F6" activeDot={{ r: 8 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="flex justify-center items-center h-64 text-sm text-gray-500">
                No data available for chart
              </div>
            )}
          </div>
          
          {/* Bar Chart */}
          <div className="bg-white shadow rounded-lg p-6 lg:col-span-3">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Average Daily Stress</h2>
            
            {barChartData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={barChartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis domain={[0, 3.5]} ticks={[1, 2, 3]} tickFormatter={(value) => {
                      switch(value) {
                        case 1: return 'Low';
                        case 2: return 'Medium';
                        case 3: return 'High';
                        default: return '';
                      }
                    }} />
                    <Tooltip 
                      formatter={(value, name) => [value.toFixed(2), 'Average Stress']}
                      labelFormatter={(label) => `Date: ${label}`}
                    />
                    <Legend />
                    <Bar dataKey="avgStress" name="Average Stress" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="flex justify-center items-center h-64 text-sm text-gray-500">
                No data available for chart
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EmployeeDetail;
