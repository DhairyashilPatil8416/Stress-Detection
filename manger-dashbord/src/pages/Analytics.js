import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import StressService from '../services/stress.service';
import ErrorDisplay from '../components/ErrorDisplay';

// Colors for stress levels
const STRESS_COLORS = {
  'Low': '#10B981', // green
  'Medium': '#F59E0B', // amber
  'High': '#EF4444' // red
};

// For pie chart
const COLORS = [STRESS_COLORS.Low, STRESS_COLORS.Medium, STRESS_COLORS.High];

const Analytics = () => {
  const [aggregateData, setAggregateData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Fetch aggregate stress data
  const fetchAggregateData = async () => {
    setLoading(true);
    setError(null); // Clear previous errors
    
    try {
      console.log('Analytics - Fetching aggregate data');
      const result = await StressService.getAggregateStressData();
      console.log('Analytics - Received result:', result);
      
      if (result.success) {
        console.log('Analytics - Setting data:', result.data);
        
        if (!result.data || 
            ((!result.data.distribution && !result.data.overall) || 
             ((!result.data.timeline && !result.data.timeseries && !result.data.dailyTrend) || 
              (result.data.timeline?.length === 0 && result.data.timeseries?.length === 0 && result.data.dailyTrend?.length === 0)))) {
          console.error('Analytics - No data available in response');
          setError('No analytics data available. There might not be enough stress records in the system yet.');
          setAggregateData(null);
        } else {
          setAggregateData({ ...result.data, _refreshKey: Date.now() });
          setError(null);
        }
      } else {
        console.error('Analytics - API returned error:', result.message);
        setError('Failed to fetch analytics data: ' + result.message);
        setAggregateData(null);
      }
    } catch (err) {
      console.error('Analytics - Unexpected error:', err);
      setError('An unexpected error occurred: ' + (err.message || err));
      setAggregateData(null);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchAggregateData();
  }, []);
  
  // Prepare data for pie chart
  const pieData = (aggregateData?.distribution || aggregateData?.overall) ? [
    { name: 'Low', value: (aggregateData.distribution?.Low || aggregateData.overall?.low_stress_count) || 0 },
    { name: 'Medium', value: (aggregateData.distribution?.Medium || aggregateData.overall?.medium_stress_count) || 0 },
    { name: 'High', value: (aggregateData.distribution?.High || aggregateData.overall?.high_stress_count) || 0 }
  ] : [];
  
  // Prepare data for bar chart
  const barData = aggregateData?.dailyTrend || aggregateData?.timeline || [];
  
  // Custom pie chart label
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index, name }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    
    return (
      <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
        {`${name} ${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };
  
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Company Stress Analytics</h1>
        <p className="mt-1 text-sm text-gray-500">
          Understand stress patterns across your organization
        </p>
      </div>
      
      {/* Controls */}
      <div className="mb-6 flex justify-end">
        <button
          onClick={fetchAggregateData}
          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg className="mr-1 -ml-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh Data
        </button>
      </div>
      
      {loading && !aggregateData ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <ErrorDisplay message={error} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Stress Distribution Card */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Stress Level Distribution</h2>
            
            {pieData.length > 0 ? (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={renderCustomizedLabel}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value} readings`, 'Count']} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="flex justify-center items-center h-72 text-sm text-gray-500">
                No data available for chart
              </div>
            )}
            
            {/* Summary Stats */}
            {aggregateData?.summary && (
              <div className="mt-6 grid grid-cols-3 gap-4 border-t border-gray-200 pt-4">
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-500">Total Readings</p>
                  <p className="mt-1 text-xl font-semibold text-gray-900">{aggregateData.summary.totalReadings}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-500">Employees Monitored</p>
                  <p className="mt-1 text-xl font-semibold text-gray-900">{aggregateData.summary.uniqueEmployees}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-500">Avg. Readings/Employee</p>
                  <p className="mt-1 text-xl font-semibold text-gray-900">
                    {aggregateData.summary.uniqueEmployees ? 
                      (aggregateData.summary.totalReadings / aggregateData.summary.uniqueEmployees).toFixed(1) :
                      '0'
                    }
                  </p>
                </div>
              </div>
            )}
          </div>
          
          {/* Daily Trend Chart */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Daily Stress Trend</h2>
            
            {barData.length > 0 ? (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={barData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="Low" name="Low Stress" fill={STRESS_COLORS.Low} stackId="a" />
                    <Bar dataKey="Medium" name="Medium Stress" fill={STRESS_COLORS.Medium} stackId="a" />
                    <Bar dataKey="High" name="High Stress" fill={STRESS_COLORS.High} stackId="a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="flex justify-center items-center h-72 text-sm text-gray-500">
                No data available for chart
              </div>
            )}
          </div>
          
          {/* Department Comparison (if available) */}
          {aggregateData?.departmentComparison && aggregateData.departmentComparison.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6 lg:col-span-2">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Department Comparison</h2>
              
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={aggregateData.departmentComparison}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    layout="vertical"
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="department" type="category" width={150} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="lowPercentage" name="Low Stress %" fill={STRESS_COLORS.Low} stackId="a" />
                    <Bar dataKey="mediumPercentage" name="Medium Stress %" fill={STRESS_COLORS.Medium} stackId="a" />
                    <Bar dataKey="highPercentage" name="High Stress %" fill={STRESS_COLORS.High} stackId="a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Analytics;
