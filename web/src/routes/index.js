import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Receipts from '../pages/Receipts';
import ReceiptDetail from '../pages/ReceiptDetail';

const PrivateRoute = ({ children }) => {
  var token = localStorage.getItem('token');

  const isAuthenticated = token; // Check if user is authenticated
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const AppRoutes = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/receipts"
          element={
            <PrivateRoute>
              <Receipts />
            </PrivateRoute>
          }
        />
        <Route
          path="/receipts/:id"
          element={
            <PrivateRoute>
              <ReceiptDetail />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/receipts" />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRoutes;