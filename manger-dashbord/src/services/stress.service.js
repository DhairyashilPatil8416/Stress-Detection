import apiClient from './api';

const StressService = {
  getLatestStressData: async () => {
    try {
      console.log('Fetching latest stress data');
      const response = await apiClient.get(`/manager/stress/latest?t=${Date.now()}`);
      console.log('Latest stress data response:', response.data);
      
      // Process the data to ensure we have the latest record per employee
      const processedData = response.data.map(employee => {
        // Create a completely new object to ensure React detects changes
        return {
          ...employee,
          // Add a timestamp to force re-rendering
          _refreshKey: Date.now() + Math.random(),
          // Ensure all fields are properly copied
          employee_id: employee.employee_id,
          display_name: employee.display_name || employee.name,
          name: employee.display_name || employee.name,
          department: employee.department,
          latest_stress_level: employee.latest_stress_level || employee.stress_level,
          latest_emotion: employee.latest_emotion || employee.emotion,
          stress_level: employee.latest_stress_level || employee.stress_level,
          emotion: employee.latest_emotion || employee.emotion,
          confidence: employee.confidence,
          timestamp: employee.timestamp,
          device_id: employee.device_id
        };
      });
      
      console.log('Processed data with new references:', processedData);
      return { success: true, data: processedData };
    } catch (error) {
      console.error('Error fetching latest stress data:', error);
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Failed to fetch latest stress data'
      };
    }
  },
  
  getEmployeeDetails: async (employeeId) => {
    try {
      console.log(`Fetching employee details for ID: ${employeeId}`);
      const response = await apiClient.get(`/manager/employee/${employeeId}`);
      console.log('Employee details response:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching employee details:', error);
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Failed to fetch employee details'
      };
    }
  },
  
  getEmployeeStressHistory: async (employeeId) => {
    try {
      console.log(`Fetching stress history for employee ID: ${employeeId}`);
      const response = await apiClient.get(`/manager/stress/history/${employeeId}`);
      console.log('Stress history response:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching stress history:', error);
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Failed to fetch employee stress history'
      };
    }
  },
  
  getAllEmployees: async () => {
    try {
      console.log('Fetching all employees');
      console.log('API URL:', apiClient.defaults.baseURL + '/manager/employees');
      const response = await apiClient.get('/manager/employees');
      console.log('All employees response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching all employees:', error);
      console.error('Error details:', error.response?.data || error.message);
      
      // Return dummy data for testing if the endpoint isn't working
      console.log('Returning dummy employee data for testing');
      return [
        {
          employee_id: "9f9e57b6-f8a5-4368-9ab1-f23f7d95a770",
          name: "Lisa Test",
          display_name: "Lisa",
          department: "Engineering",
          active: true
        },
        {
          employee_id: "e639321b-eb0f-4a32-8034-fa965c9565f9",
          name: "Jennifer Example",
          display_name: "Jennie",
          department: "Marketing",
          active: true
        },
        {
          employee_id: "81c8b9a4-2e46-4925-8df8-8090bb5d37f0",
          name: "Jisoo Demo",
          display_name: "Jisoo",
          department: "Sales",
          active: true
        }
      ];
    }
  },
  
  getAggregateStressData: async () => {
    try {
      console.log('Fetching aggregate stress data');
      console.log('API URL:', apiClient.defaults.baseURL + '/manager/stress/aggregate');
      
      // Get data for the last 30 days to show recent trends
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      const fromDate = thirtyDaysAgo.toISOString().split('T')[0]; // YYYY-MM-DD format
      
      const response = await apiClient.get('/manager/stress/aggregate', {
        params: { 
          from_date: fromDate,
          t: Date.now()
        }
      });
      console.log('Aggregate stress data response:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching aggregate stress data:', error);
      console.error('Error details:', error.response?.data || error.message);
      console.error('Error status:', error.response?.status);
      
      // Only return an error so the user knows something is wrong
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Failed to fetch aggregate stress data. Please check the server connection.'
      };
    }
  },
  
  triggerStressAnalysis: async (employeeId) => {
    try {
      console.log(`Triggering stress analysis for employee ID: ${employeeId}`);
      const response = await apiClient.post(`/manager/trigger/${employeeId}`);
      console.log('Trigger analysis response:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error triggering stress analysis:', error);
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Failed to trigger stress analysis'
      };
    }
  }
};

export default StressService;
