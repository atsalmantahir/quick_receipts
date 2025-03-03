import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CButton, CForm, CFormInput, CFormLabel, CFormTextarea, CSpinner, CAlert } from '@coreui/react';
import { createReceipt } from '../../api/receipts'; // Import your API function
import Loader from '../../components/Common/Loader'; // Import the Loader component
import MainLayout from '../../components/MainLayout'; // Import MainLayout

const CreateReceipt = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [receipt, setReceipt] = useState({
    name: "",
    description: "",
    amount: "",
    file: null, // For file upload
  });

  const handleInput = (event) => {
    const { name, value } = event.target;
    setReceipt({ ...receipt, [name]: value });
  };

  const handleFileChange = (event) => {
    setReceipt({ ...receipt, file: event.target.files[0] });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      setIsLoading(true);

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('name', receipt.name);
      formData.append('description', receipt.description);
      formData.append('amount', receipt.amount);
      if (receipt.file) {
        formData.append('file', receipt.file);
      }

      // Call the API to create the receipt
      await createReceipt(formData);

      // Reset form and redirect
      setReceipt({ name: "", description: "", amount: "", file: null });
      navigate('/receipts'); // Redirect to receipts list
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
            <CFormLabel htmlFor="name">Name</CFormLabel>
            <CFormInput
              type="text"
              id="name"
              name="name"
              value={receipt.name}
              onChange={handleInput}
              required
            />
          </div>
          <div className="mb-3">
            <CFormLabel htmlFor="description">Description</CFormLabel>
            <CFormTextarea
              id="description"
              name="description"
              value={receipt.description}
              onChange={handleInput}
            />
          </div>
          <div className="mb-3">
            <CFormLabel htmlFor="amount">Amount</CFormLabel>
            <CFormInput
              type="number"
              id="amount"
              name="amount"
              value={receipt.amount}
              onChange={handleInput}
              required
            />
          </div>
          <div className="mb-3">
            <CFormLabel htmlFor="file">Upload File</CFormLabel>
            <CFormInput
              type="file"
              id="file"
              name="file"
              onChange={handleFileChange}
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