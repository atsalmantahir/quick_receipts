import axios from 'axios';

const API_URL = 'https://yourapi.com/receipts';

const getReceipts = async () => {
  const response = await axios.get(API_URL, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  return response.data;
};

const createReceipt = async (data) => {
  const response = await axios.post(API_URL, data, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  return response.data;
};

const updateReceipt = async (id, data) => {
  const response = await axios.put(`${API_URL}/${id}`, data, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  return response.data;
};

const deleteReceipt = async (id) => {
  const response = await axios.delete(`${API_URL}/${id}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  return response.data;
};

const getReceiptById = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  return response.data;
};

export { getReceipts, createReceipt, updateReceipt, deleteReceipt, getReceiptById };