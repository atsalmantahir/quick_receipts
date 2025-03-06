import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Receipts from '../pages/receipts/Receipts';
import ReceiptDetail from '../pages/receipts/ReceiptDetail';
import CreateReceipt from '../pages/receipts/CreateReceipt';
import ExtractReceipt from '../pages/receipts/ExtractReceipt';
import Dashboard from '../pages/Dashboard';

const PrivateRoute = ({ children }) => {
  var token = localStorage.getItem('token');

  const isAuthenticated = token; // Check if user is authenticated
  return isAuthenticated ? children : <Navigate to="/dashboard" />;
};

const AppRoutes = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
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
          path="/receipts/new" // New route for creating a receipt
          element={
            <PrivateRoute>
              <CreateReceipt />
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
        <Route path="/receipts/extract/:id" element={<PrivateRoute><ExtractReceipt /></PrivateRoute>} /> 

        <Route path="*" element={<Navigate to="/receipts" />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRoutes;