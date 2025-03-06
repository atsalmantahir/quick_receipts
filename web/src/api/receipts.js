import apiClient from './index';

const RECEIPTS_URL = '/receipts';

const getReceipts = async () => {
  const response = await apiClient.get(RECEIPTS_URL);
  return response.data;
};

const createReceipt = async (data) => {
  const response = await apiClient.post(`${RECEIPTS_URL}/`, data);
  return response.data;
};

const updateReceipt = async (id, data) => {
  const response = await apiClient.put(`${RECEIPTS_URL}/${id}`, data);
  return response.data;
};

const deleteReceipt = async (id) => {
  const response = await apiClient.delete(`${RECEIPTS_URL}/${id}`);
  return response.data;
};

const getReceiptById = async (id) => {
  const response = await apiClient.get(`${RECEIPTS_URL}/${id}`);
  return response.data;
};

export { getReceipts, createReceipt, updateReceipt, deleteReceipt, getReceiptById };