import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { login } from '../api/auth';
import { CContainer, CCard, CCardBody, CForm, CFormInput, CButton, CAlert } from '@coreui/react';

const Login = () => {
  const navigate = useNavigate();

  const initialValues = {
    email: '',
    password: '',
  };

  const validationSchema = Yup.object({
    email: Yup.string().email('Invalid email address').required('Email is required'),
    password: Yup.string().required('Password is required'),
  });

  const handleSubmit = async (values, { setSubmitting, setErrors }) => {
    try {
      const { token } = await login(values.email, values.password);
      localStorage.setItem('token', token); // Save token to localStorage
      navigate('/receipts'); // Redirect to receipts page
    } catch (error) {
      console.error('Login failed', error);
      // Display a user-friendly error message
      setErrors({ email: 'Invalid email or password', password: 'Invalid email or password' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <CContainer className="d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
      <CCard style={{ width: '400px' }}>
        <CCardBody>
          <h1 className="text-center mb-4">Login</h1>
          <Formik initialValues={initialValues} validationSchema={validationSchema} onSubmit={handleSubmit}>
            {({ isSubmitting, errors, touched }) => (
              <CForm>
                {/* Email Field */}
                <div className="mb-3">
                  <label htmlFor="email" className="form-label">
                    Email
                  </label>
                  <Field
                    as={CFormInput}
                    type="email"
                    name="email"
                    id="email"
                    placeholder="Enter your email"
                    className={touched.email && errors.email ? 'is-invalid' : ''}
                  />
                  <ErrorMessage name="email" component="div" className="invalid-feedback" />
                </div>

                {/* Password Field */}
                <div className="mb-3">
                  <label htmlFor="password" className="form-label">
                    Password
                  </label>
                  <Field
                    as={CFormInput}
                    type="password"
                    name="password"
                    id="password"
                    placeholder="Enter your password"
                    className={touched.password && errors.password ? 'is-invalid' : ''}
                  />
                  <ErrorMessage name="password" component="div" className="invalid-feedback" />
                </div>

                {/* Submit Button */}
                <div className="d-grid">
                  <CButton type="submit" color="primary" disabled={isSubmitting}>
                    {isSubmitting ? 'Logging in...' : 'Login'}
                  </CButton>
                </div>

                {/* Display API errors */}
                {errors.api && (
                  <CAlert color="danger" className="mt-3">
                    {errors.api}
                  </CAlert>
                )}

                {/* Register Link */}
                <div className="text-center mt-3">
                  <p>
                    Don't have an account?{' '}
                    <CButton color="link" onClick={() => navigate('/register')}>
                      Register
                    </CButton>
                  </p>
                </div>
              </CForm>
            )}
          </Formik>
        </CCardBody>
      </CCard>
    </CContainer>
  );
};

export default Login;