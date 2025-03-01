import React, { useState } from 'react';
import {
  CContainer,
  CHeader,
  CHeaderBrand,
  CHeaderToggler,
  CSidebar,
  CSidebarBrand,
  CSidebarNav,
  CSidebarToggler,
  CNavItem,
  CNavLink,
  CButton,
  CBreadcrumb,
  CBreadcrumbItem,
} from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { cilMenu, cilAccountLogout } from '@coreui/icons';
import { useNavigate } from 'react-router-dom';

const MainLayout = ({ children, breadcrumbs }) => {
  const [sidebarVisible, setSidebarVisible] = useState(true); // State to toggle sidebar
  const navigate = useNavigate();

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('token'); // Clear the token
    navigate('/login'); // Redirect to login page
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <CSidebar
        position="fixed"
        visible={sidebarVisible}
        onVisibleChange={(visible) => setSidebarVisible(visible)}
        style={{ backgroundColor: '#343a40', width: '250px' }} // Dark background and fixed width
        colorScheme="dark" // Dark theme for sidebar
      >
        <CSidebarBrand className="text-white p-3">My App</CSidebarBrand>
        <CSidebarNav>
          <CNavItem>
            <CNavLink href="/dashboard" className="text-white">
              Dashboard
            </CNavLink>
          </CNavItem>
          <CNavItem>
            <CNavLink href="/receipts" className="text-white">
              Receipts
            </CNavLink>
          </CNavItem>
          <CNavItem>
            <CNavLink href="/settings" className="text-white">
              Settings
            </CNavLink>
          </CNavItem>
        </CSidebarNav>
        <CSidebarToggler onClick={() => setSidebarVisible(!sidebarVisible)} />
      </CSidebar>

      {/* Main Content */}
      <div
        style={{
          flex: 1,
          marginLeft: sidebarVisible ? '250px' : '0', // Adjust margin based on sidebar visibility
          transition: 'margin-left 0.3s',
          padding: '20px', // Add padding for better alignment
        }}
      >
        {/* Header */}
        <CHeader position="sticky" className="mb-4">
          <CContainer fluid>
            <CHeaderToggler onClick={() => setSidebarVisible(!sidebarVisible)}>
              <CIcon icon={cilMenu} className="text-white" />
            </CHeaderToggler>
            <CHeaderBrand>My App</CHeaderBrand>
            <CButton color="danger" onClick={handleLogout}>
              <CIcon icon={cilAccountLogout} /> Logout
            </CButton>
          </CContainer>
        </CHeader>

        {/* Breadcrumbs */}
        <CContainer fluid>
          <CBreadcrumb className="my-3">
            {breadcrumbs.map((crumb, index) => (
              <CBreadcrumbItem key={index} href={crumb.path} active={index === breadcrumbs.length - 1}>
                {crumb.name}
              </CBreadcrumbItem>
            ))}
          </CBreadcrumb>

          {/* Page Content */}
          {children}
        </CContainer>
      </div>
    </div>
  );
};

export default MainLayout;