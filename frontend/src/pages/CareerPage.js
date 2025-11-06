import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import axios from 'axios';
import { Briefcase, MapPin, DollarSign, Clock, Building } from 'lucide-react';
import { toast } from 'sonner';

const CareerPage = () => {
  const { companySlug } = useParams();
  const navigate = useNavigate();
  const [company, setCompany] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

  useEffect(() => {
    fetchCompanyAndJobs();
  }, [companySlug]);

  const fetchCompanyAndJobs = async () => {
    try {
      // Fetch company
      const companyResponse = await axios.get(`${API_URL}/companies/slug/${companySlug}`);
      setCompany(companyResponse.data);

      // Fetch active jobs
      const jobsResponse = await axios.get(`${API_URL}/jobs/company/${companyResponse.data.id}?status=active`);
      setJobs(jobsResponse.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('Company not found');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Company not found</h1>
          <p className="text-gray-600">The company you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  const branding = company.branding || {};
  const primaryColor = branding.primary_color || '#3B82F6';

  return (
    <div className="min-h-screen bg-gray-50" data-testid="career-page">
      {/* Header */}
      <div 
        className="bg-gradient-to-r py-20 px-6"
        style={{
          background: `linear-gradient(135deg, ${primaryColor} 0%, ${branding.secondary_color || '#8B5CF6'} 100%)`
        }}
      >
        <div className="container mx-auto max-w-6xl">
          <div className="flex items-center space-x-6 mb-6">
            {branding.logo_url && (
              <img src={branding.logo_url} alt={company.name} className="h-20 w-20 rounded-lg bg-white p-2" />
            )}
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">{company.name}</h1>
              <p className="text-xl text-white/90">{company.industry}</p>
            </div>
          </div>
          {company.description && (
            <p className="text-lg text-white/90 max-w-3xl">{company.description}</p>
          )}
        </div>
      </div>

      {/* About Section */}
      {branding.about_us && (
        <div className="py-16 px-6 bg-white">
          <div className="container mx-auto max-w-6xl">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">About Us</h2>
            <p className="text-lg text-gray-700 leading-relaxed">{branding.about_us}</p>
          </div>
        </div>
      )}

      {/* Jobs Section */}
      <div className="py-16 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="mb-10">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Open Positions</h2>
            <p className="text-gray-600">
              {jobs.length === 0 ? 'No open positions at the moment' : `${jobs.length} open position${jobs.length !== 1 ? 's' : ''}`}
            </p>
          </div>

          {jobs.length === 0 ? (
            <Card>
              <CardContent className="py-16 text-center">
                <Briefcase className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No open positions</h3>
                <p className="text-gray-600">Check back later for new opportunities</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {jobs.map((job) => (
                <Card 
                  key={job.id} 
                  className="hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => navigate(`/apply/${job.id}`)}
                  data-testid={`job-${job.id}`}
                >
                  <CardHeader>
                    <CardTitle className="text-xl">{job.title}</CardTitle>
                    <div className="flex items-center gap-2 text-sm text-gray-600 mt-2">
                      <Building className="w-4 h-4" />
                      {job.department}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="secondary">
                        {job.job_type.replace('_', ' ')}
                      </Badge>
                      <Badge variant="secondary">
                        {job.experience_level}
                      </Badge>
                    </div>

                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex items-center">
                        <MapPin className="w-4 h-4 mr-2" />
                        {job.location_type.charAt(0).toUpperCase() + job.location_type.slice(1)}
                        {job.location && ` - ${job.location}`}
                      </div>

                      {job.salary_min && job.salary_max && (
                        <div className="flex items-center">
                          <DollarSign className="w-4 h-4 mr-2" />
                          ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()} {job.salary_currency}
                        </div>
                      )}

                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-2" />
                        Posted {new Date(job.created_at).toLocaleDateString()}
                      </div>
                    </div>

                    <p className="text-sm text-gray-700 line-clamp-3 mt-4">
                      {job.description}
                    </p>

                    <Button className="w-full mt-4" data-testid={`apply-btn-${job.id}`}>
                      Apply Now
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="py-10 px-6 bg-gray-900 text-white">
        <div className="container mx-auto max-w-6xl text-center">
          <p>&copy; 2025 {company.name}. All rights reserved.</p>
          {company.website && (
            <p className="mt-2">
              <a href={company.website} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                Visit our website
              </a>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default CareerPage;
