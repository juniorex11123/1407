import axios from 'axios';

// Get backend URL from environment
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API_URL = `${API_BASE_URL}/api`;

console.log('🔍 API Configuration:', { API_BASE_URL, API_URL });

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/panel';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username, password) => {
    console.log('🔍 authAPI.login called with:', { username, password: '***' });
    try {
      const response = await api.post('/auth/login', { username, password });
      console.log('✅ authAPI.login response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ authAPI.login error:', error);
      throw error;
    }
  },
};

// Companies API
export const companiesAPI = {
  getAll: async () => {
    const response = await api.get('/companies');
    return response.data;
  },
  
  create: async (company) => {
    const response = await api.post('/companies', company);
    return response.data;
  },
  
  update: async (id, company) => {
    const response = await api.put(`/companies/${id}`, company);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/companies/${id}`);
    return response.data;
  },
};

// Users API
export const usersAPI = {
  getAll: async () => {
    const response = await api.get('/users');
    return response.data;
  },
  
  create: async (user) => {
    const response = await api.post('/users', user);
    return response.data;
  },
  
  update: async (id, user) => {
    const response = await api.put(`/users/${id}`, user);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/users/${id}`);
    return response.data;
  },
};

// Employees API
export const employeesAPI = {
  getAll: async () => {
    const response = await api.get('/employees');
    return response.data;
  },
  
  create: async (employee) => {
    const response = await api.post('/employees', employee);
    return response.data;
  },
  
  update: async (id, employee) => {
    const response = await api.put(`/employees/${id}`, employee);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/employees/${id}`);
    return response.data;
  },
  
  generateQR: async (id) => {
    const response = await api.get(`/employees/${id}/qr`);
    return response.data;
  },
  
  downloadQRPDF: async (id, employeeName) => {
    try {
      console.log('Downloading PDF for employee:', employeeName, 'ID:', id);
      console.log('API URL:', API_URL);
      
      const response = await api.get(`/employees/${id}/qr-pdf`, {
        responseType: 'blob'
      });
      
      console.log('Response received:', response.status);
      
      // Create download link
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const safeName = employeeName.replace(/[^a-zA-Z0-9]/g, '_');
      link.download = `qr_code_${safeName}.pdf`;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('PDF download completed successfully');
      return response.data;
    } catch (error) {
      console.error('Error downloading PDF:', error);
      throw error;
    }
  },
};

// Time Entries API
export const timeEntriesAPI = {
  getAll: async () => {
    const response = await api.get('/time-entries');
    return response.data;
  },
  
  create: async (timeEntry) => {
    const response = await api.post('/time-entries', timeEntry);
    return response.data;
  },
  
  update: async (id, timeEntry) => {
    const response = await api.put(`/time-entries/${id}`, timeEntry);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/time-entries/${id}`);
    return response.data;
  },
};

// Employee Summary API
export const employeeSummaryAPI = {
  getSummary: async (month, year) => {
    const params = new URLSearchParams();
    if (month) params.append('month', month);
    if (year) params.append('year', year);
    
    const response = await api.get(`/employee-summary?${params}`);
    return response.data;
  },
  
  getEmployeeMonths: async (employeeId) => {
    const response = await api.get(`/employee-months/${employeeId}`);
    return response.data;
  },
  
  getEmployeeDays: async (employeeId, yearMonth) => {
    const response = await api.get(`/employee-days/${employeeId}/${yearMonth}`);
    return response.data;
  },
};

export default api;