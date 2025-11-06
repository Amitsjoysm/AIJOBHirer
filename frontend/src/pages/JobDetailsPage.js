import React from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';

const JobDetailsPage = () => {
  return (
    <DashboardLayout>
      <div data-testid="job-details-page">
        <h1 className="text-3xl font-bold">Job Details</h1>
      </div>
    </DashboardLayout>
  );
};

export default JobDetailsPage;
