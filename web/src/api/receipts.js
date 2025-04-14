import apiClient from './index';

const RECEIPTS_URL = '/receipts';

const getReceipts = async (page = 1, perPage = 10) => {
  const response = await apiClient.get(`${RECEIPTS_URL}?page=${page}&per_page=${perPage}`);
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

// Perform OCR on a receipt image
const performOCR = async (id) => {
  const response = await apiClient.post(`${RECEIPTS_URL}/${id}/ocr`);
  return response.data;
};

const getOcrData = async (id) => {
    const response = await apiClient.get(`${RECEIPTS_URL}/${id}/ocr`);
    return response.data;
};

const getReceiptPreviewUrl = async (filename) => {
    const response = await apiClient.get(`${RECEIPTS_URL}/preview/${filename}`);
    console.log(response)
    return response.data;
};

export { getReceipts, createReceipt, updateReceipt, deleteReceipt, getReceiptById, performOCR, getOcrData, getReceiptPreviewUrl };