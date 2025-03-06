import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getReceiptById } from '../../api/receipts'; // Import API functions
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

  // Sample OCR data (temporary)
  const sampleOcrData = [
    { type: 'purchase_time', text_value: '15:30:05', normalized_value: '', confidence: 0.95 },
    { type: 'total_amount', text_value: '836', normalized_value: '836', confidence: 0.98 },
    { type: 'supplier_phone', text_value: '047-460-3821-', normalized_value: '', confidence: 0.92 },
    { type: 'total_tax_amount', text_value: '76', normalized_value: '76', confidence: 0.97 },
    { type: 'net_amount', text_value: '760', normalized_value: '760', confidence: 0.96 },
    { type: 'supplier_name', text_value: 'STARBUCKSⓇ', normalized_value: '', confidence: 0.94 },
    { type: 'receipt_date', text_value: '2021/07/11 15:30:05', normalized_value: '2021-07-11', confidence: 0.99 },
    { type: 'payment_type', text_value: 'ックスカード', normalized_value: '', confidence: 0.91 },
    { type: 'line_item', text_value: '1 G アイス スターバックス ラテ 420', normalized_value: '', confidence: 0.93 },
    { type: 'line_item/quantity', text_value: '1', normalized_value: '', confidence: 0.95 },
    { type: 'line_item/description', text_value: 'G アイス スターバックス ラテ', normalized_value: '', confidence: 0.94 },
    { type: 'line_item/amount', text_value: '420', normalized_value: '420', confidence: 0.97 },
    { type: 'currency', text_value: '', normalized_value: 'JPY', confidence: 0.99 },
    { type: 'supplier_address', text_value: '', normalized_value: '日本\n〒273-0005 千葉県船橋市本町７丁目１−１ シャポー船橋本館 1階', confidence: 0.98 },
    { type: 'supplier_city', text_value: '', normalized_value: '船橋市', confidence: 0.98 },
  ];

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

  // Simulate OCR process with sample data
  const handlePerformOCR = async () => {
    try {
      setIsOcrLoading(true); // Start OCR loading
      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setOcrResults(sampleOcrData); // Use sample OCR data
    } catch (error) {
      setError('Failed to perform OCR: ' + error.message);
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
      result.type,
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
                  color="success"
                  onClick={handleDownloadCSV}
                  disabled={ocrResults.length === 0} // Disable if no OCR results
                >
                  Download as CSV
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
                        <CTableDataCell>{result.type}</CTableDataCell>
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