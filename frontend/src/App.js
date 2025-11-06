import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from './components/ui/sonner';
import './App.css';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import JobsPage from './pages/JobsPage';
import CreateJobPage from './pages/CreateJobPage';
import JobDetailsPage from './pages/JobDetailsPage';
import ApplicationsPage from './pages/ApplicationsPage';
import ApplicationDetailsPage from './pages/ApplicationDetailsPage';
import CandidatesPage from './pages/CandidatesPage';
import CandidateDetailPage from './pages/CandidateDetailPage';
import InterviewsPage from './pages/InterviewsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/EnhancedSettingsPage';
import CareerPage from './pages/CareerPage';
import ApplyPage from './pages/ApplyPage';
import { GoogleCallbackPage, MicrosoftCallbackPage } from './pages/OAuthCallbackPage';

// Context
import { AuthProvider, useAuth } from './context/AuthContext';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return user ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
            <Route path="/auth/microsoft/callback" element={<MicrosoftCallbackPage />} />
            <Route path="/careers/:companySlug" element={<CareerPage />} />
            <Route path="/apply/:jobId" element={<ApplyPage />} />
            
            {/* Private routes */}
            <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
            <Route path="/jobs" element={<PrivateRoute><JobsPage /></PrivateRoute>} />
            <Route path="/jobs/create" element={<PrivateRoute><CreateJobPage /></PrivateRoute>} />
            <Route path="/jobs/:jobId" element={<PrivateRoute><JobDetailsPage /></PrivateRoute>} />
            <Route path="/applications" element={<PrivateRoute><ApplicationsPage /></PrivateRoute>} />
            <Route path="/applications/:applicationId" element={<PrivateRoute><ApplicationDetailsPage /></PrivateRoute>} />
            <Route path="/candidates" element={<PrivateRoute><CandidatesPage /></PrivateRoute>} />
            <Route path="/interviews" element={<PrivateRoute><InterviewsPage /></PrivateRoute>} />
            <Route path="/analytics" element={<PrivateRoute><AnalyticsPage /></PrivateRoute>} />
            <Route path="/settings" element={<PrivateRoute><SettingsPage /></PrivateRoute>} />
          </Routes>
          <Toaster position="top-right" expand={false} richColors />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
