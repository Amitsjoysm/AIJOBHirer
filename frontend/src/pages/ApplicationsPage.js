import React from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';

const ApplicationsPage = () => {
  return (
    <DashboardLayout>
      <div data-testid="applications-page">
        <h1 className="text-3xl font-bold">Applications</h1>
        <p className="text-gray-600 mt-2">Review and manage applications</p>
      </div>
    </DashboardLayout>
  );
};

export default ApplicationsPage;
