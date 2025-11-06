import React from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';

const ApplicationDetailsPage = () => {
  return (
    <DashboardLayout>
      <div data-testid="application-details-page">
        <h1 className="text-3xl font-bold">Application Details</h1>
      </div>
    </DashboardLayout>
  );
};

export default ApplicationDetailsPage;
