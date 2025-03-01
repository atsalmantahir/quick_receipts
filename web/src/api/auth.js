import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api/auth'; // Replace with your API base URL

const login = async (email, password) => {
  const response = await axios.post(`${API_URL}/login`, { email, password }, {
    headers: {
      'Content-Type': 'application/json', // Ensure JSON content type
    },
  });
  return response.data;
};

const register = async (userData) => {
  const response = await axios.post(`${API_URL}/register`, userData, {
    headers: {
      'Content-Type': 'application/json', // Ensure JSON content type
    },
  });
  return response.data;
};

export { login, register };