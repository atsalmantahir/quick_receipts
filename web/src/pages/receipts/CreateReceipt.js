import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CButton, CForm, CFormInput, CFormLabel, CSpinner, CAlert } from '@coreui/react';
import { createReceipt } from '../../api/receipts'; // Import your API function
import Loader from '../../components/Common/Loader'; // Import the Loader component
import MainLayout from '../../components/MainLayout'; // Import MainLayout

const CreateReceipt = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [file, setFile] = useState(null); // State for the uploaded file

  const handleFileChange = (event) => {
    setFile(event.target.files[0]); // Set the selected file
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      setIsLoading(true);

      // Check if a file is selected
      if (!file) {
        setError('No file selected');
        return;
      }

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('receipt_image', file); // Match the key expected by the backend

      // Call the API to create the receipt
      const response = await createReceipt(formData);

      // Handle success
      if (response.message === 'Receipt created successfully') {
        navigate('/receipts'); // Redirect to receipts list
      } else {
        setError(response.message || 'Failed to create receipt');
      }
    } catch (error) {
      setError(error.message || 'Failed to create receipt. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <MainLayout
      breadcrumbs={[
        { name: 'Home', path: '/' },
        { name: 'Receipts', path: '/receipts' },
        { name: 'Create Receipt', path: '/receipts/new' },
      ]}
    >
      <div className="receipt-form">
        <div className="heading">
          {isLoading && <Loader />} {/* Use the Loader component here */}
          {error && (
            <CAlert color="danger" closeButton>
              {error}
            </CAlert>
          )}
          <h1>Create Receipt</h1>
        </div>
        <CForm onSubmit={handleSubmit}>
          <div className="mb-3">
            <CFormLabel htmlFor="file">Upload Receipt Image</CFormLabel>
            <CFormInput
              type="file"
              id="file"
              name="file"
              onChange={handleFileChange}
              required
            />
          </div>
          <CButton type="submit" color="primary" disabled={isLoading}>
            {isLoading ? <CSpinner size="sm" /> : 'Submit'}
          </CButton>
        </CForm>
      </div>
    </MainLayout>
  );
};

export default CreateReceipt;