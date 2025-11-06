import React from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';

const InterviewsPage = () => {
  return (
    <DashboardLayout>
      <div data-testid="interviews-page">
        <h1 className="text-3xl font-bold">Interviews</h1>
        <p className="text-gray-600 mt-2">Schedule and manage interviews</p>
      </div>
    </DashboardLayout>
  );
};

export default InterviewsPage;
