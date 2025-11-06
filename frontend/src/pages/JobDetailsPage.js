import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import axios from 'axios';
import { ArrowLeft, Edit, Eye, Users, ExternalLink, Share2 } from 'lucide-react';
import { toast } from 'sonner';

const JobDetailsPage = () => {
  const { jobId } = useParams();
  const { API_URL, getAuthHeaders } = useAuth();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJob();
  }, [jobId]);

  const fetchJob = async () => {
    try {
      const response = await axios.get(`${API_URL}/jobs/${jobId}`, {
        headers: getAuthHeaders()
      });
      setJob(response.data);

      // Fetch company
      const companyResponse = await axios.get(`${API_URL}/companies/${response.data.company_id}`, {
        headers: getAuthHeaders()
      });
      setCompany(companyResponse.data);
    } catch (error) {
      console.error('Failed to fetch job:', error);
      toast.error('Failed to load job');
    } finally {
      setLoading(false);
    }
  };

  const copyJobLink = () => {
    const link = `${window.location.origin}/apply/${jobId}`;
    navigator.clipboard.writeText(link);
    toast.success('Job link copied to clipboard!');
  };

  const getStatusColor = (status) => {
    const colors = {
      active: 'bg-green-100 text-green-700',
      draft: 'bg-gray-100 text-gray-700',
      paused: 'bg-yellow-100 text-yellow-700',
      closed: 'bg-red-100 text-red-700'
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
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

  if (!job) {
    return (
      <DashboardLayout>
        <div className="text-center py-16">
          <p className="text-gray-600">Job not found</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div data-testid="job-details-page" className="max-w-5xl">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/jobs')}
          className="mb-6"
          data-testid="back-btn"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Jobs
        </Button>

        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
              <Badge className={getStatusColor(job.status)}>
                {job.status}
              </Badge>
            </div>
            <p className="text-gray-600">{job.department} • {job.location_type}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={copyJobLink} data-testid="share-btn">
              <Share2 className="w-4 h-4 mr-2" />
              Share
            </Button>
            <Button onClick={() => navigate(`/jobs/${jobId}/edit`)} data-testid="edit-btn">
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Views</p>
                  <p className="text-2xl font-bold text-gray-900">{job.view_count || 0}</p>
                </div>
                <Eye className="w-8 h-8 text-indigo-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Applications</p>
                  <p className="text-2xl font-bold text-gray-900">{job.application_count || 0}</p>
                </div>
                <Users className="w-8 h-8 text-indigo-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <Button 
                className="w-full" 
                onClick={() => navigate(`/applications?job=${jobId}`)}
                data-testid="view-applications-btn"
              >
                View Applications
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Job Details */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Job Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
              <p className="text-gray-700 whitespace-pre-line">{job.description}</p>
            </div>

            {job.requirements?.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Requirements</h3>
                <ul className="list-disc list-inside space-y-1">
                  {job.requirements.map((req, index) => (
                    <li key={index} className="text-gray-700">{req}</li>
                  ))}
                </ul>
              </div>
            )}

            {job.nice_to_have?.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Nice to Have</h3>
                <ul className="list-disc list-inside space-y-1">
                  {job.nice_to_have.map((item, index) => (
                    <li key={index} className="text-gray-700">{item}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 pt-4 border-t">
              <div>
                <p className="text-sm text-gray-600 mb-1">Job Type</p>
                <p className="font-medium text-gray-900">{job.job_type.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Experience Level</p>
                <p className="font-medium text-gray-900">{job.experience_level}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Location</p>
                <p className="font-medium text-gray-900">
                  {job.location_type} {job.location && `- ${job.location}`}
                </p>
              </div>
              {job.salary_min && job.salary_max && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Salary Range</p>
                  <p className="font-medium text-gray-900">
                    ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()} {job.salary_currency}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Screening Questions */}
        {job.screening_questions?.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Screening Questions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {job.screening_questions.map((q, index) => (
                  <div key={index} className="pb-4 border-b last:border-b-0 last:pb-0">
                    <div className="flex items-start justify-between">
                      <p className="font-medium text-gray-900">{q.question}</p>
                      {q.required && (
                        <Badge variant="secondary">Required</Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">Type: {q.question_type}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Public Link */}
        {job.status === 'active' && (
          <Card>
            <CardHeader>
              <CardTitle>Public Application Link</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <code className="flex-1 px-4 py-2 bg-gray-50 rounded text-sm">
                  {window.location.origin}/apply/{jobId}
                </code>
                <Button variant="outline" size="sm" onClick={copyJobLink}>
                  Copy
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => window.open(`/apply/${jobId}`, '_blank')}
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Open
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
};

export default JobDetailsPage;
