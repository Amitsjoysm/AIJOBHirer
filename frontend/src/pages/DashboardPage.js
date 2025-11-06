import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import axios from 'axios';
import { Briefcase, FileText, Users, Calendar, Plus, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

const DashboardPage = () => {
  const { API_URL, getAuthHeaders } = useAuth();
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_URL}/analytics/dashboard`, {
        headers: getAuthHeaders()
      });
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      toast.error('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      title: 'Active Jobs',
      value: analytics?.active_jobs || 0,
      icon: <Briefcase className="w-8 h-8 text-indigo-600" />,
      bg: 'bg-indigo-50',
      testId: 'stat-active-jobs'
    },
    {
      title: 'Total Applications',
      value: analytics?.total_applications || 0,
      icon: <FileText className="w-8 h-8 text-purple-600" />,
      bg: 'bg-purple-50',
      testId: 'stat-total-applications'
    },
    {
      title: 'Shortlisted',
      value: analytics?.shortlisted_candidates || 0,
      icon: <Users className="w-8 h-8 text-green-600" />,
      bg: 'bg-green-50',
      testId: 'stat-shortlisted'
    },
    {
      title: 'Interviews Scheduled',
      value: analytics?.interviews_scheduled || 0,
      icon: <Calendar className="w-8 h-8 text-blue-600" />,
      bg: 'bg-blue-50',
      testId: 'stat-interviews'
    },
  ];

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="spinner"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div data-testid="dashboard-page">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">Welcome back! Here's your hiring overview.</p>
          </div>
          <Button onClick={() => navigate('/jobs/create')} data-testid="create-job-btn">
            <Plus className="w-5 h-5 mr-2" />
            Create Job
          </Button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow" data-testid={stat.testId}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                    <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <div className={`p-3 rounded-lg ${stat.bg}`}>
                    {stat.icon}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Applications</CardTitle>
            </CardHeader>
            <CardContent>
              {analytics?.recent_applications?.length > 0 ? (
                <div className="space-y-4">
                  {analytics.recent_applications.slice(0, 5).map((app) => (
                    <div
                      key={app.id}
                      className="flex items-center justify-between p-4 rounded-lg bg-gray-50 hover:bg-gray-100 cursor-pointer"
                      onClick={() => navigate(`/applications/${app.id}`)}
                      data-testid={`application-${app.id}`}
                    >
                      <div>
                        <p className="font-medium text-gray-900">{app.candidate_name}</p>
                        <p className="text-sm text-gray-600">Applied {new Date(app.created_at).toLocaleDateString()}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        app.status === 'shortlisted' ? 'bg-green-100 text-green-700' :
                        app.status === 'submitted' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {app.status}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No applications yet</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Button className="w-full justify-start" variant="outline" onClick={() => navigate('/jobs/create')} data-testid="quick-create-job">
                  <Plus className="w-5 h-5 mr-2" />
                  Create New Job Posting
                </Button>
                <Button className="w-full justify-start" variant="outline" onClick={() => navigate('/applications')} data-testid="quick-view-applications">
                  <FileText className="w-5 h-5 mr-2" />
                  View All Applications
                </Button>
                <Button className="w-full justify-start" variant="outline" onClick={() => navigate('/candidates')} data-testid="quick-view-candidates">
                  <Users className="w-5 h-5 mr-2" />
                  Browse Candidates
                </Button>
                <Button className="w-full justify-start" variant="outline" onClick={() => navigate('/analytics')} data-testid="quick-view-analytics">
                  <TrendingUp className="w-5 h-5 mr-2" />
                  View Analytics
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
