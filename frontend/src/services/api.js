import axios from 'axios';

// Get backend URL from environment
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API_URL = `${API_BASE_URL}/api`;

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
    const response = await api.post('/auth/login', { username, password });
    return response.data;
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
    const response = await api.post(`/employees/${id}/qr`);
    return response.data;
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

export default api;