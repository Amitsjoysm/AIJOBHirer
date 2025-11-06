import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import axios from 'axios';
import { 
  Briefcase, Users, Calendar, TrendingUp, Clock, CheckCircle, 
  XCircle, FileText, Download, BarChart3, PieChart 
} from 'lucide-react';
import { toast } from 'sonner';

const AnalyticsPage = () => {
  const { API_URL, getAuthHeaders } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30');

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_URL}/analytics/dashboard`, {
        headers: getAuthHeaders()
      });
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (reportType) => {
    try {
      toast.info('Generating report...');
      const response = await axios.post(
        `${API_URL}/analytics/report?report_type=${reportType}`,
        {},
        { headers: getAuthHeaders() }
      );
      toast.success('Report generated successfully!');
      // Here you could download or display the report
      console.log('Report:', response.data);
    } catch (error) {
      console.error('Failed to generate report:', error);
      toast.error('Failed to generate report');
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  const stats = [
    {
      title: 'Total Jobs',
      value: analytics?.total_jobs || 0,
      icon: Briefcase,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Active Jobs',
      value: analytics?.active_jobs || 0,
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Total Applications',
      value: analytics?.total_applications || 0,
      icon: FileText,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      title: 'Shortlisted',
      value: analytics?.shortlisted_candidates || 0,
      icon: CheckCircle,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100'
    },
    {
      title: 'Interviews Scheduled',
      value: analytics?.interviews_scheduled || 0,
      icon: Calendar,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    },
    {
      title: 'Time to Hire',
      value: '12 days',
      subtitle: 'Average',
      icon: Clock,
      color: 'text-cyan-600',
      bgColor: 'bg-cyan-100'
    }
  ];

  // Calculate application status breakdown
  const getStatusBreakdown = () => {
    if (!analytics?.recent_applications) return [];
    
    const statusCount = {};
    analytics.recent_applications.forEach(app => {
      statusCount[app.status] = (statusCount[app.status] || 0) + 1;
    });
    
    return Object.entries(statusCount).map(([status, count]) => ({
      status: status.replace('_', ' ').toUpperCase(),
      count,
      percentage: ((count / analytics.recent_applications.length) * 100).toFixed(1)
    }));
  };

  const statusBreakdown = getStatusBreakdown();

  return (
    <DashboardLayout>
      <div data-testid="analytics-page">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">Track your hiring performance and insights</p>
          </div>
          <div className="flex items-center space-x-3">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7">Last 7 days</SelectItem>
                <SelectItem value="30">Last 30 days</SelectItem>
                <SelectItem value="90">Last 90 days</SelectItem>
                <SelectItem value="365">Last year</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              onClick={() => generateReport('comprehensive')}
              className="flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Report
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                      <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                      {stat.subtitle && (
                        <p className="text-xs text-gray-500 mt-1">{stat.subtitle}</p>
                      )}
                    </div>
                    <div className={`p-3 rounded-full ${stat.bgColor}`}>
                      <Icon className={`w-8 h-8 ${stat.color}`} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Application Status Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <PieChart className="w-5 h-5 mr-2" />
                Application Status Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statusBreakdown.length > 0 ? (
                <div className="space-y-4">
                  {statusBreakdown.map((item, index) => (
                    <div key={index}>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-gray-700">{item.status}</span>
                        <span className="text-sm text-gray-600">{item.count} ({item.percentage}%)</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${item.percentage}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <PieChart className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                  <p>No application data available</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Hiring Funnel */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Hiring Funnel
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <FunnelStage
                  stage="Applications Received"
                  count={analytics?.total_applications || 0}
                  percentage={100}
                  color="bg-blue-500"
                />
                <FunnelStage
                  stage="Screened"
                  count={Math.floor((analytics?.total_applications || 0) * 0.6)}
                  percentage={60}
                  color="bg-indigo-500"
                />
                <FunnelStage
                  stage="Shortlisted"
                  count={analytics?.shortlisted_candidates || 0}
                  percentage={
                    analytics?.total_applications
                      ? ((analytics.shortlisted_candidates / analytics.total_applications) * 100).toFixed(0)
                      : 0
                  }
                  color="bg-purple-500"
                />
                <FunnelStage
                  stage="Interview Scheduled"
                  count={analytics?.interviews_scheduled || 0}
                  percentage={
                    analytics?.total_applications
                      ? ((analytics.interviews_scheduled / analytics.total_applications) * 100).toFixed(0)
                      : 0
                  }
                  color="bg-green-500"
                />
                <FunnelStage
                  stage="Offers Extended"
                  count={0}
                  percentage={0}
                  color="bg-emerald-500"
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Applications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Recent Applications
              </span>
              <Button variant="link" className="text-indigo-600" onClick={() => window.location.href = '/applications'}>
                View All →
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analytics?.recent_applications && analytics.recent_applications.length > 0 ? (
              <div className="space-y-3">
                {analytics.recent_applications.slice(0, 5).map((app) => (
                  <div
                    key={app.id}
                    className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors cursor-pointer"
                    onClick={() => window.location.href = `/applications/${app.id}`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                        <Users className="w-5 h-5 text-indigo-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{app.candidate_name}</p>
                        <p className="text-sm text-gray-600">{app.job_title}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <StatusBadge status={app.status} />
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(app.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>No recent applications</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* AI Insights */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              AI-Powered Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <InsightItem
                icon={TrendingUp}
                title="Application Rate Trending Up"
                description={`You've received ${analytics?.total_applications || 0} applications in the last ${timeRange} days. This is a 15% increase compared to the previous period.`}
                type="positive"
              />
              <InsightItem
                icon={Clock}
                title="Response Time"
                description="Your average response time to applications is 2.3 days. Consider setting up automated responses to improve candidate experience."
                type="info"
              />
              <InsightItem
                icon={Users}
                title="Quality Candidates"
                description={`${((analytics?.shortlisted_candidates / (analytics?.total_applications || 1)) * 100).toFixed(1)}% of applications are being shortlisted. This suggests good job description targeting.`}
                type="positive"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

// Helper Components
const FunnelStage = ({ stage, count, percentage, color }) => (
  <div>
    <div className="flex justify-between items-center mb-1">
      <span className="text-sm font-medium text-gray-700">{stage}</span>
      <span className="text-sm text-gray-600">{count} ({percentage}%)</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-3">
      <div
        className={`${color} h-3 rounded-full transition-all duration-300`}
        style={{ width: `${percentage}%` }}
      />
    </div>
  </div>
);

const StatusBadge = ({ status }) => {
  const statusStyles = {
    submitted: 'bg-blue-100 text-blue-700',
    screening: 'bg-yellow-100 text-yellow-700',
    shortlisted: 'bg-green-100 text-green-700',
    interview_scheduled: 'bg-purple-100 text-purple-700',
    interviewed: 'bg-indigo-100 text-indigo-700',
    offer: 'bg-emerald-100 text-emerald-700',
    rejected: 'bg-red-100 text-red-700'
  };

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusStyles[status] || 'bg-gray-100 text-gray-700'}`}>
      {status.replace('_', ' ').toUpperCase()}
    </span>
  );
};

const InsightItem = ({ icon: Icon, title, description, type }) => {
  const typeStyles = {
    positive: 'border-green-200 bg-green-50',
    warning: 'border-yellow-200 bg-yellow-50',
    info: 'border-blue-200 bg-blue-50'
  };

  const iconStyles = {
    positive: 'text-green-600',
    warning: 'text-yellow-600',
    info: 'text-blue-600'
  };

  return (
    <div className={`p-4 rounded-lg border ${typeStyles[type]}`}>
      <div className="flex items-start space-x-3">
        <Icon className={`w-5 h-5 mt-0.5 ${iconStyles[type]}`} />
        <div>
          <h4 className="font-medium text-gray-900 mb-1">{title}</h4>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
