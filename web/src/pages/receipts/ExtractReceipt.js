import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getReceiptById } from '../../api/receipts'; // API function to fetch receipt data
import { CSpinner, CAlert, CCard, CCardHeader, CCardBody, CButton, CRow, CCol, CTable, CTableHead, CTableRow, CTableHeaderCell, CTableBody, CTableDataCell } from '@coreui/react';
import MainLayout from '../../components/MainLayout'; // Import MainLayout

const ExtractReceipt = () => {
  const { id } = useParams(); // Get the receipt ID from the URL
  const [isLoading, setIsLoading] = useState(true);
  const [receiptData, setReceiptData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getReceiptById(id); // Call the API to fetch receipt data
        setReceiptData(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [id]);

  if (isLoading) {
    return <CSpinner />;
  }

  if (error) {
    return <CAlert color="danger">{error}</CAlert>;
  }

  return (
    <MainLayout
      breadcrumbs={[
        { name: 'Home', path: '/' },
        { name: 'Receipts', path: '/receipts' },
        { name: 'Extract Receipt', path: `/receipts/extract/${id}` },
      ]}
    >
      <CRow className="mb-4">
        <CCol>
          <h1>Extract Receipt</h1>
          <p className="text-medium-emphasis">Receipt ID: {id}</p>
        </CCol>
      </CRow>

      <CRow>
        <CCol>
          <CCard>
            <CCardHeader>
              <h5>Receipt Details</h5>
            </CCardHeader>
            <CCardBody>
              <CTable striped bordered hover responsive>
                <CTableHead>
                  <CTableRow>
                    <CTableHeaderCell>Field</CTableHeaderCell>
                    <CTableHeaderCell>Value</CTableHeaderCell>
                  </CTableRow>
                </CTableHead>
                <CTableBody>
                  <CTableRow>
                    <CTableDataCell>Receipt ID</CTableDataCell>
                    <CTableDataCell>{receiptData.receipt_id}</CTableDataCell>
                  </CTableRow>
                  <CTableRow>
                    <CTableDataCell>User ID</CTableDataCell>
                    <CTableDataCell>{receiptData.user_id}</CTableDataCell>
                  </CTableRow>
                  <CTableRow>
                    <CTableDataCell>Total Amount</CTableDataCell>
                    <CTableDataCell>${receiptData.total_amount}</CTableDataCell>
                  </CTableRow>
                  <CTableRow>
                    <CTableDataCell>Receipt Date</CTableDataCell>
                    <CTableDataCell>
                      {new Date(receiptData.receipt_date).toLocaleDateString()}
                    </CTableDataCell>
                  </CTableRow>
                  <CTableRow>
                    <CTableDataCell>Receipt Image</CTableDataCell>
                    <CTableDataCell>
                      <img
                        src={receiptData.receipt_image_url}
                        alt="Receipt"
                        style={{ maxWidth: '100%', height: 'auto', maxHeight: '200px' }}
                      />
                    </CTableDataCell>
                  </CTableRow>
                </CTableBody>
              </CTable>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>

      <CRow className="mt-4">
        <CCol>
          <CButton color="primary" onClick={() => window.history.back()}>
            Back to Receipts
          </CButton>
        </CCol>
      </CRow>
    </MainLayout>
  );
};

export default ExtractReceipt;