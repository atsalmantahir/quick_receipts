import axios from 'axios';

// Create a base Axios instance
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:5000/api', // Base URL for all API requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the token in headers (except for login and register)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  const isAuthEndpoint = config.url.includes('/auth/login') || config.url.includes('/auth/register');

  if (token && !isAuthEndpoint) {
    // config.headers.Authorization = `Bearer ${token}`;
  }
  
  return config;
});

export default apiClient;