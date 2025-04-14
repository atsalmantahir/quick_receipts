import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getReceiptById, performOCR, getOcrData, getReceiptPreviewUrl } from '../../api/receipts'; // Import API functions
import { CSpinner, CAlert, CCard, CCardHeader, CCardBody, CButton, CRow, CCol, CTable, CTableHead, CTableRow, CTableHeaderCell, CTableBody, CTableDataCell } from '@coreui/react';
import MainLayout from '../../components/MainLayout';
import { saveAs } from 'file-saver'; // For downloading CSV

const ExtractReceipt = () => {
  const { id } = useParams(); // Get the receipt ID from the URL
  const [isLoading, setIsLoading] = useState(true);
  const [receiptData, setReceiptData] = useState(null);
  const [ocrResults, setOcrResults] = useState([]); // State for OCR results
  const [isOcrLoading, setIsOcrLoading] = useState(false); // State for OCR loading
  const [error, setError] = useState(null);

  // Fetch receipt data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getReceiptById(id); // Fetch receipt data
        setReceiptData(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [id]);

  // Perform OCR on the receipt
  const handlePerformOCR = async () => {
    try {
      setIsOcrLoading(true); // Start OCR loading
      const response = await performOCR(id); // Call the performOCR API
      setOcrResults(response.ocr_results); // Set OCR results from the API response
    } catch (error) {
      setError('Failed to perform OCR: ' + error.message);
    } finally {
      setIsOcrLoading(false); // Stop OCR loading
    }
  };

  // Fetch OCR data for the receipt
  const handleFetchOcrData = async () => {
    try {
      setIsOcrLoading(true); // Start OCR loading
      const response = await getOcrData(id); // Call the getOcrData API
      setOcrResults(response.ocr_details); // Set OCR results from the API response
    } catch (error) {
      setError('Failed to fetch OCR data: ' + error.message);
    } finally {
      setIsOcrLoading(false); // Stop OCR loading
    }
  };

  // Download OCR results as CSV
  const handleDownloadCSV = () => {
    if (ocrResults.length === 0) {
      alert('No OCR results available to download.');
      return;
    }

    // Create CSV content
    const headers = ['Type', 'Text Value', 'Normalized Value', 'Confidence'];
    const rows = ocrResults.map((result) => [
      result.field_type,
      result.text_value,
      result.normalized_value,
      `${(result.confidence * 100).toFixed(2)}%`,
    ]);

    const csvContent = [
      headers.join(','), // Add headers
      ...rows.map((row) => row.join(',')), // Add rows
    ].join('\n');

    // Create a Blob and trigger download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, `receipt_${id}_ocr_results.csv`);
  };

  // New method: Yayoi-compatible CSV
  const handleDownloadYayoiCSV = () => {
    if (ocrResults.length === 0) {
      alert('No OCR results available.');
      return;
    }

    // Transform data for Yayoi
    const yayoiData = ocrResults.reduce((acc, item) => {
      switch (item.field_type) {
        case 'receipt_date':
          acc.取引日 = item.normalized_value?.replace(/(\d{4})(\d{3})(\d{2})/, '$1$2$3'); // Fix date format
          break;
        case 'line_item':
          acc.items.push({
            品名: item.text_value,
            数量: 1,
            金額: 0,
            税区分: '課税',
          });
          break;
        case 'line_item/amount':
          if (acc.items.length > 0) {
            const lastItem = acc.items[acc.items.length - 1];
            lastItem.金額 = parseInt(item.text_value.replace(/,/g, '')) || 0;
          }
          break;
        case 'total_amount':
          acc.items.push({
            品名: '合計金額',
            金額: parseInt(item.text_value.replace(/,/g, '')) || 0,
            税区分: '課税',
          });
          break;
      }
      return acc;
    }, { items: [] });

    // Create CSV content
    const headers = ['取引日', '品名', '数量', '金額', '税区分'];
    const rows = [
      [yayoiData.取引日 || '', '', '', '', ''], // Header row with date
      ...yayoiData.items.map((item) => [
        item.品名,
        item.数量,
        item.金額,
        item.税区分,
      ]),
    ];

    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, `yayoi_receipt_${id}.csv`);
  };

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

      <CRow className="mb-4">
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
                    <CTableDataCell>Receipt Date</CTableDataCell>
                    <CTableDataCell>
                      {new Date(receiptData.receipt_date).toLocaleDateString()}
                    </CTableDataCell>
                  </CTableRow>
                  <CTableRow>
                    <CTableDataCell>Confidence score</CTableDataCell>
                    <CTableDataCell>{receiptData.confidence_score}</CTableDataCell>
                  </CTableRow>
                  <CTableRow>
                    <CTableDataCell>Total Amount</CTableDataCell>
                    <CTableDataCell>{receiptData.total_amount}</CTableDataCell>
                  </CTableRow>
                  <CTableRow>
                    <CTableDataCell>Receipt Image</CTableDataCell>
                    <CTableDataCell>
                    <a
                      href={`http://127.0.0.1:5000/api/receipts/preview/${receiptData.receipt_image_url}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <img
                        src={`http://127.0.0.1:5000/api/receipts/preview/${receiptData.receipt_image_url}`}
                        alt="Receipt"
                        style={{ maxWidth: '100%', height: 'auto', maxHeight: '200px' }}
                      />
                    </a>
                    </CTableDataCell>
                  </CTableRow>
                </CTableBody>
              </CTable>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>

      <CRow className="mb-4">
        <CCol>
          <CCard>
            <CCardHeader>
              <h5>OCR Results</h5>
              <div className="d-flex gap-2">
                <CButton
                  color="primary"
                  onClick={handlePerformOCR}
                  disabled={isOcrLoading} // Disable button while OCR is in progress
                >
                  {isOcrLoading ? <CSpinner size="sm" /> : 'Perform OCR'}
                </CButton>
                <CButton
                  color="secondary"
                  onClick={handleFetchOcrData}
                  disabled={isOcrLoading} // Disable button while fetching OCR data
                >
                  {isOcrLoading ? <CSpinner size="sm" /> : 'Fetch OCR Data'}
                </CButton>
                <CButton
                  color="success"
                  onClick={handleDownloadCSV}
                  disabled={ocrResults.length === 0} // Disable if no OCR results
                >
                  Download as CSV
                </CButton>
                <CButton
                  color="warning"
                  onClick={handleDownloadYayoiCSV}
                  disabled={ocrResults.length === 0}
                >
                  Download Yayoi CSV
                </CButton>
              </div>
            </CCardHeader>
            <CCardBody>
              <CTable striped bordered hover responsive>
                <CTableHead>
                  <CTableRow>
                    <CTableHeaderCell>Type</CTableHeaderCell>
                    <CTableHeaderCell>Text Value</CTableHeaderCell>
                    <CTableHeaderCell>Normalized Value</CTableHeaderCell>
                    <CTableHeaderCell>Confidence</CTableHeaderCell>
                  </CTableRow>
                </CTableHead>
                <CTableBody>
                  {ocrResults.length > 0 ? (
                    ocrResults.map((result, index) => (
                      <CTableRow key={index}>
                        <CTableDataCell>{result.field_type}</CTableDataCell>
                        <CTableDataCell>{result.text_value}</CTableDataCell>
                        <CTableDataCell>{result.normalized_value}</CTableDataCell>
                        <CTableDataCell>{(result.confidence * 100).toFixed(2)}%</CTableDataCell>
                      </CTableRow>
                    ))
                  ) : (
                    <CTableRow>
                      <CTableDataCell colSpan="4" className="text-center">
                        No OCR results available. Click "Perform OCR" to extract data.
                      </CTableDataCell>
                    </CTableRow>
                  )}
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
