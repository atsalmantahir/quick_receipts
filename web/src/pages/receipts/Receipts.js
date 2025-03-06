import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getReceipts, deleteReceipt } from '../../api/receipts';
import { CButton, CTable, CTableHead, CTableRow, CTableHeaderCell, CTableBody, CTableDataCell, CModal, CModalHeader, CModalTitle, CModalBody, CModalFooter } from '@coreui/react';
import MainLayout from '../../components/MainLayout';

const Receipts = () => {
  const [receipts, setReceipts] = useState([]);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
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

  const handlePreview = (fileUrl) => {
    setPreviewUrl(fileUrl);
    setIsPreviewModalOpen(true);
  };

  const closePreviewModal = () => {
    setIsPreviewModalOpen(false);
    setPreviewUrl(null);
  };

  const handleExtract = (receiptId) => {
    // Redirect to the Extract Receipt screen with the receipt ID as a parameter
    navigate(`/receipts/extract/${receiptId}`);
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
            <CTableRow key={receipt.receipt_id}>
              <CTableDataCell>{index + 1}</CTableDataCell>
              <CTableDataCell>{receipt.receipt_image_url}</CTableDataCell>
              <CTableDataCell>
                <CButton
                  color="info"
                  size="sm"
                  onClick={() => navigate(`/receipts/${receipt.receipt_id}`)}
                  className="me-2"
                >
                  Edit
                </CButton>
                <CButton
                  color="danger"
                  size="sm"
                  onClick={() => handleDelete(receipt.receipt_id)}
                  className="me-2"
                >
                  Delete
                </CButton>
                <CButton
                  color="success"
                  size="sm"
                  onClick={() => handlePreview(receipt.receipt_image_url)}
                  className="me-2"
                >
                  Preview
                </CButton>
                <CButton
                  color="warning"
                  size="sm"
                  onClick={() => handleExtract(receipt.receipt_id)} // Redirect to Extract Receipt screen
                >
                  Extract
                </CButton>
              </CTableDataCell>
            </CTableRow>
          ))}
        </CTableBody>
      </CTable>

      {/* Preview Modal */}
      <CModal visible={isPreviewModalOpen} onClose={closePreviewModal} size="lg">
        <CModalHeader>
          <CModalTitle>Receipt Preview</CModalTitle>
        </CModalHeader>
        <CModalBody>
          {previewUrl && (
            <>
              {previewUrl.endsWith('.pdf') ? (
                <iframe
                  src={previewUrl}
                  width="100%"
                  height="500px"
                  title="PDF Preview"
                />
              ) : (
                <img
                  src={previewUrl}
                  alt="Receipt Preview"
                  style={{ maxWidth: '100%', height: 'auto' }}
                />
              )}
            </>
          )}
        </CModalBody>
        <CModalFooter>
          <CButton color="secondary" onClick={closePreviewModal}>
            Close
          </CButton>
        </CModalFooter>
      </CModal>
    </MainLayout>
  );
};

export default Receipts;