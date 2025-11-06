import React from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';

const AnalyticsPage = () => {
  return (
    <DashboardLayout>
      <div data-testid="analytics-page">
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-gray-600 mt-2">View hiring metrics and insights</p>
      </div>
    </DashboardLayout>
  );
};

export default AnalyticsPage;
