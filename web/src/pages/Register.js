import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { register } from '../api/auth';
import { CContainer, CCard, CCardBody, CFormInput, CButton, CAlert } from '@coreui/react';
import '@coreui/coreui/dist/css/coreui.min.css'; // Ensure CoreUI CSS is imported

const Register = () => {
  const navigate = useNavigate();

  const initialValues = {
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  };

  const validationSchema = Yup.object({
    email: Yup.string().email('Invalid email address').required('Email is required'),
    password: Yup.string()
      .required('Password is required')
      .min(6, 'Password must be at least 6 characters'),
    confirmPassword: Yup.string()
      .oneOf([Yup.ref('password'), null], 'Passwords must match')
      .required('Confirm Password is required'),
  });

  const handleSubmit = async (values, { setSubmitting, setErrors }) => {
    try {
      console.log('Submitting form with values:', values); // Debugging
      await register(values); // Call the register API
      navigate('/login'); // Redirect to login page after successful registration
    } catch (error) {
      console.error('Registration failed', error);
      setErrors({ api: error.response?.data?.message || 'Registration failed. Please try again.' }); // Display API error
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <CContainer className="d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
      <CCard style={{ width: '400px' }}>
        <CCardBody>
          <h1 className="text-center mb-4">Register</h1>
          <Formik initialValues={initialValues} validationSchema={validationSchema} onSubmit={handleSubmit}>
            {({ isSubmitting, errors, touched }) => (
              <Form>
                
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

                {/* Confirm Password Field */}
                <div className="mb-3">
                  <label htmlFor="confirmPassword" className="form-label">
                    Confirm Password
                  </label>
                  <Field
                    as={CFormInput}
                    type="password"
                    name="confirmPassword"
                    id="confirmPassword"
                    placeholder="Confirm your password"
                    className={touched.confirmPassword && errors.confirmPassword ? 'is-invalid' : ''}
                  />
                  <ErrorMessage name="confirmPassword" component="div" className="invalid-feedback" />
                </div>

                {/* Submit Button */}
                <div className="d-grid">
                  <CButton type="submit" color="primary" disabled={isSubmitting}>
                    {isSubmitting ? 'Registering...' : 'Register'}
                  </CButton>
                </div>

                {/* Display API errors */}
                {errors.api && (
                  <CAlert color="danger" className="mt-3">
                    {errors.api}
                  </CAlert>
                )}

                {/* Login Link */}
                <div className="text-center mt-3">
                  <p>
                    Already have an account?{' '}
                    <CButton color="link" onClick={() => navigate('/login')}>
                      Login
                    </CButton>
                  </p>
                </div>
              </Form>
            )}
          </Formik>
        </CCardBody>
      </CCard>
    </CContainer>
  );
};

export default Register;