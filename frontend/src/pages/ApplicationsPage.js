import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import axios from 'axios';
import { Search, FileText, Star } from 'lucide-react';
import { toast } from 'sonner';

const ApplicationsPage = () => {
  const { API_URL, getAuthHeaders } = useAuth();
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedJob, setSelectedJob] = useState('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch jobs first
      const jobsResponse = await axios.get(`${API_URL}/jobs/my-jobs`, {
        headers: getAuthHeaders()
      });
      setJobs(jobsResponse.data);

      // Fetch all applications for all jobs
      const allApplications = [];
      for (const job of jobsResponse.data) {
        try {
          const appsResponse = await axios.get(`${API_URL}/applications/job/${job.id}`, {
            headers: getAuthHeaders()
          });
          allApplications.push(...appsResponse.data.map(app => ({ ...app, job_title: job.title })));
        } catch (err) {
          console.error(`Failed to fetch applications for job ${job.id}`);
        }
      }
      setApplications(allApplications);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  const filteredApplications = applications.filter(app => {
    const matchesSearch = app.candidate_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         app.candidate_email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || app.status === statusFilter;
    const matchesJob = selectedJob === 'all' || app.job_id === selectedJob;
    return matchesSearch && matchesStatus && matchesJob;
  });

  const getStatusColor = (status) => {
    const colors = {
      submitted: 'bg-blue-100 text-blue-700',
      screening: 'bg-yellow-100 text-yellow-700',
      shortlisted: 'bg-green-100 text-green-700',
      interview_scheduled: 'bg-purple-100 text-purple-700',
      interviewed: 'bg-indigo-100 text-indigo-700',
      offer: 'bg-emerald-100 text-emerald-700',
      rejected: 'bg-red-100 text-red-700'
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

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
      <div data-testid="applications-page">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Applications</h1>
          <p className="text-gray-600 mt-1">Review and manage job applications</p>
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <Input
                placeholder="Search by name or email..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                data-testid="search-applications-input"
              />
            </div>
          </div>
          <Select value={selectedJob} onValueChange={setSelectedJob}>
            <SelectTrigger className="w-[200px]" data-testid="job-filter">
              <SelectValue placeholder="All Jobs" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Jobs</SelectItem>
              {jobs.map((job) => (
                <SelectItem key={job.id} value={job.id}>{job.title}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px]" data-testid="status-filter">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="submitted">Submitted</SelectItem>
              <SelectItem value="screening">Screening</SelectItem>
              <SelectItem value="shortlisted">Shortlisted</SelectItem>
              <SelectItem value="interview_scheduled">Interview Scheduled</SelectItem>
              <SelectItem value="interviewed">Interviewed</SelectItem>
              <SelectItem value="offer">Offer</SelectItem>
              <SelectItem value="rejected">Rejected</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Applications List */}
        {filteredApplications.length === 0 ? (
          <Card>
            <CardContent className="py-16 text-center">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No applications found</h3>
              <p className="text-gray-600">Applications will appear here as candidates apply to your jobs</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredApplications.map((app) => (
              <Card 
                key={app.id} 
                className="hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/applications/${app.id}`)}
                data-testid={`application-${app.id}`}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 flex-1">
                      <Avatar className="h-12 w-12">
                        <AvatarFallback className="bg-indigo-100 text-indigo-600 font-semibold">
                          {app.candidate_name.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <h3 className="font-semibold text-gray-900">{app.candidate_name}</h3>
                          {app.ai_evaluation?.recommendation === 'strong_match' && (
                            <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                          )}
                        </div>
                        <p className="text-sm text-gray-600">{app.candidate_email}</p>
                        <div className="flex items-center gap-4 mt-2">
                          <span className="text-sm text-gray-500">
                            Applied to: <span className="font-medium">{app.job_title}</span>
                          </span>
                          <span className="text-sm text-gray-500">
                            {new Date(app.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      {app.ai_evaluation?.overall_score && (
                        <div className="text-center">
                          <div className={`text-2xl font-bold ${getScoreColor(app.ai_evaluation.overall_score)}`}>
                            {Math.round(app.ai_evaluation.overall_score)}
                          </div>
                          <div className="text-xs text-gray-500">AI Score</div>
                        </div>
                      )}
                      
                      <Badge className={getStatusColor(app.status)}>
                        {app.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>

                  {app.ai_evaluation?.summary && (
                    <div className="mt-4 pt-4 border-t">
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {app.ai_evaluation.summary}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default ApplicationsPage;
