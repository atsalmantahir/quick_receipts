import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { getReceiptById, updateReceipt, deleteReceipt } from '../../api/receipts';
import { CContainer, CCard, CCardBody, CForm, CFormInput, CButton } from '@coreui/react';

const ReceiptDetail = () => {
  const { id } = useParams(); // Get the receipt ID from the URL
  const navigate = useNavigate();
  const [receipt, setReceipt] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  // Fetch receipt details on component mount
  useEffect(() => {
    const fetchReceipt = async () => {
      try {
        const data = await getReceiptById(id);
        setReceipt(data);
      } catch (error) {
        console.error('Failed to fetch receipt', error);
      }
    };
    fetchReceipt();
  }, [id]);

  // Handle receipt update
  const handleUpdate = async (values) => {
    try {
      await updateReceipt(id, values);
      setIsEditing(false); // Exit edit mode
      setReceipt(values); // Update local state
    } catch (error) {
      console.error('Failed to update receipt', error);
    }
  };

  // Handle receipt deletion
  const handleDelete = async () => {
    try {
      await deleteReceipt(id);
      navigate('/receipts'); // Redirect to receipts list
    } catch (error) {
      console.error('Failed to delete receipt', error);
    }
  };

  // Validation schema for the form
  const validationSchema = Yup.object({
    title: Yup.string().required('Title is required'),
    amount: Yup.number().required('Amount is required').positive('Amount must be positive'),
    date: Yup.date().required('Date is required'),
  });

  if (!receipt) return <div>Loading...</div>;

  
  return (
    <CContainer>
      <CCard>
        <CCardBody>
          <h1>Receipt Details</h1>
          {isEditing ? (
            <Formik
              initialValues={receipt}
              validationSchema={validationSchema}
              onSubmit={handleUpdate}
            >
              {({ isSubmitting }) => (
                <CForm>
                  <div className="mb-3">
                    <label>Title</label>
                    <Field as={CFormInput} type="text" name="title" />
                    <ErrorMessage name="title" component="div" className="text-danger" />
                  </div>
                  <div className="mb-3">
                    <label>Amount</label>
                    <Field as={CFormInput} type="number" name="amount" />
                    <ErrorMessage name="amount" component="div" className="text-danger" />
                  </div>
                  <div className="mb-3">
                    <label>Date</label>
                    <Field as={CFormInput} type="date" name="date" />
                    <ErrorMessage name="date" component="div" className="text-danger" />
                  </div>
                  <CButton type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Updating...' : 'Update'}
                  </CButton>
                  <CButton color="secondary" onClick={() => setIsEditing(false)}>
                    Cancel
                  </CButton>
                </CForm>
              )}
            </Formik>
          ) : (
            <div>
              <p><strong>Title:</strong> {receipt.title}</p>
              <p><strong>Amount:</strong> ${receipt.amount}</p>
              <p><strong>Date:</strong> {new Date(receipt.date).toLocaleDateString()}</p>
              <CButton color="primary" onClick={() => setIsEditing(true)}>
                Edit
              </CButton>
              <CButton color="danger" onClick={handleDelete}>
                Delete
              </CButton>
              <CButton color="secondary" onClick={() => navigate('/receipts')}>
                Back to List
              </CButton>
            </div>
          )}
        </CCardBody>
      </CCard>
    </CContainer>
  );
};

export default ReceiptDetail;