import React from 'react';
import MainLayout from '../components/MainLayout';

const Dashboard = () => {
  return (
    <MainLayout
      breadcrumbs={[
        { name: 'Home', path: '/' },
        { name: 'Dashboard', path: '/dashboard' },
      ]}
    >
      <h1>Welcome to the Dashboard</h1>
      <p>This is the homepage of your application.</p>
    </MainLayout>
  );
};

export default Dashboard;