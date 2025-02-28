import axios from 'axios';

const API_URL = 'https://yourapi.com/auth'; // Replace with your API base URL

const login = async (email, password) => {
  const response = await axios.post(`${API_URL}/login`, { email, password });
  return response.data;
};

const register = async (userData) => {
  const response = await axios.post(`${API_URL}/register`, userData);
  return response.data;
};

export { login, register };