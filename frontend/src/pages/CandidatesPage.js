import React from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';

const CandidatesPage = () => {
  return (
    <DashboardLayout>
      <div data-testid="candidates-page">
        <h1 className="text-3xl font-bold">Candidates</h1>
        <p className="text-gray-600 mt-2">Browse and manage candidates</p>
      </div>
    </DashboardLayout>
  );
};

export default CandidatesPage;
