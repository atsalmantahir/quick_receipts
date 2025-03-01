import apiClient from './index';

const AUTH_URL = '/auth';

const login = async (email, password) => {
  try {
    const response = await apiClient.post(`${AUTH_URL}/login`, { email, password });
    
    // Save the access_token to localStorage
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }

    return response.data; // Return the response data (including access_token)
  } catch (error) {
    console.error('Login failed:', error);
    throw error; // Re-throw the error for handling in the UI
  }
};
const register = async (userData) => {
  const response = await apiClient.post(`${AUTH_URL}/register`, userData);
  return response.data;
};

export { login, register };