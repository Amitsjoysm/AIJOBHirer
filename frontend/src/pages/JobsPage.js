import React from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';

const JobsPage = () => {
  return (
    <DashboardLayout>
      <div data-testid="jobs-page">
        <h1 className="text-3xl font-bold">Jobs</h1>
        <p className="text-gray-600 mt-2">Manage your job postings</p>
      </div>
    </DashboardLayout>
  );
};

export default JobsPage;
