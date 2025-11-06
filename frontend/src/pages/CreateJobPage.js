import React from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';

const CreateJobPage = () => {
  return (
    <DashboardLayout>
      <div data-testid="create-job-page">
        <h1 className="text-3xl font-bold">Create Job</h1>
        <p className="text-gray-600 mt-2">Create a new job posting with AI assistance</p>
      </div>
    </DashboardLayout>
  );
};

export default CreateJobPage;
