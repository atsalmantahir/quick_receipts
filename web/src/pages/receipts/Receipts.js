import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getReceipts, deleteReceipt } from '../../api/receipts';
import { CButton, CTable, CTableHead, CTableRow, CTableHeaderCell, CTableBody, CTableDataCell } from '@coreui/react';
import MainLayout from '../../components/MainLayout';

const Receipts = () => {
  const [receipts, setReceipts] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchReceipts();
  }, []);

  const fetchReceipts = async () => {
    const data = await getReceipts();
    setReceipts(data);
  };

  const handleDelete = async (id) => {
    await deleteReceipt(id);
    fetchReceipts();
  };

  return (
    <MainLayout
      breadcrumbs={[
        { name: 'Home', path: '/' },
        { name: 'Receipts', path: '/receipts' },
      ]}
    >
      <h1>Receipts</h1>
      <CButton color="primary" onClick={() => navigate('/receipts/new')}>
        Create New Receipt
      </CButton>

      <CTable striped bordered hover responsive className="mt-4">
        <CTableHead>
          <CTableRow>
            <CTableHeaderCell>#</CTableHeaderCell>
            <CTableHeaderCell>Name</CTableHeaderCell>
            <CTableHeaderCell>Actions</CTableHeaderCell>
          </CTableRow>
        </CTableHead>
        <CTableBody>
          {receipts.map((receipt, index) => (
            <CTableRow key={receipt.id}>
              <CTableDataCell>{index + 1}</CTableDataCell>
              <CTableDataCell>{receipt.receipt_image_url}</CTableDataCell>
              <CTableDataCell>
                <CButton
                  color="info"
                  size="sm"
                  onClick={() => navigate(`/receipts/${receipt.id}`)}
                  className="me-2"
                >
                  Edit
                </CButton>
                <CButton
                  color="danger"
                  size="sm"
                  onClick={() => handleDelete(receipt.id)}
                >
                  Delete
                </CButton>
              </CTableDataCell>
            </CTableRow>
          ))}
        </CTableBody>
      </CTable>
    </MainLayout>
  );
};

export default Receipts;