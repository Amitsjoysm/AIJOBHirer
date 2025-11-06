import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import axios from 'axios';
import { 
  ArrowLeft, Mail, Phone, Linkedin, MapPin, Briefcase, 
  GraduationCap, Award, FileText, Calendar 
} from 'lucide-react';
import { toast } from 'sonner';

const CandidateDetailPage = () => {
  const { candidateId } = useParams();
  const { API_URL, getAuthHeaders } = useAuth();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCandidateData();
  }, [candidateId]);

  const fetchCandidateData = async () => {
    try {
      // Fetch candidate details
      const candidateResponse = await axios.get(
        `${API_URL}/candidates/${candidateId}`,
        { headers: getAuthHeaders() }
      );
      setCandidate(candidateResponse.data);

      // Fetch candidate's applications
      const appsResponse = await axios.get(`${API_URL}/applications`, {
        headers: getAuthHeaders()
      });
      const candidateApps = appsResponse.data.filter(
        app => app.candidate_id === candidateId
      );
      setApplications(candidateApps);
    } catch (error) {
      console.error('Failed to fetch candidate:', error);
      toast.error('Failed to load candidate details');
    } finally {
      setLoading(false);
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

  if (!candidate) {
    return (
      <DashboardLayout>
        <div className="text-center py-16">
          <p className="text-gray-600">Candidate not found</p>
          <Button onClick={() => navigate('/candidates')} className="mt-4">
            Back to Candidates
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  const parsedResume = candidate.parsed_resume || {};

  return (
    <DashboardLayout>
      <div data-testid="candidate-detail-page">
        {/* Header */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/candidates')}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Candidates
        </Button>

        {/* Candidate Profile Card */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-6">
              <Avatar className="h-24 w-24">
                <AvatarFallback className="bg-indigo-100 text-indigo-600 text-3xl font-semibold">
                  {candidate.full_name.split(' ').map(n => n[0]).join('')}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{candidate.full_name}</h1>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-gray-600 mb-4">
                  <a href={`mailto:${candidate.email}`} className="flex items-center hover:text-indigo-600">
                    <Mail className="w-4 h-4 mr-2" />
                    {candidate.email}
                  </a>
                  
                  {candidate.phone && (
                    <a href={`tel:${candidate.phone}`} className="flex items-center hover:text-indigo-600">
                      <Phone className="w-4 h-4 mr-2" />
                      {candidate.phone}
                    </a>
                  )}
                  
                  {candidate.linkedin_url && (
                    <a 
                      href={candidate.linkedin_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center hover:text-indigo-600"
                    >
                      <Linkedin className="w-4 h-4 mr-2" />
                      LinkedIn Profile
                    </a>
                  )}
                  
                  {parsedResume.location && (
                    <div className="flex items-center">
                      <MapPin className="w-4 h-4 mr-2" />
                      {parsedResume.location}
                    </div>
                  )}
                </div>

                {candidate.resume_url && (
                  <Button 
                    variant="outline" 
                    onClick={() => window.open(candidate.resume_url, '_blank')}
                    className="flex items-center"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    Download Resume
                  </Button>
                )}
              </div>

              <div className="text-right">
                <div className="text-sm text-gray-600 mb-1">Applications</div>
                <div className="text-3xl font-bold text-indigo-600">{applications.length}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs defaultValue="summary" className="space-y-6">
          <TabsList>
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="experience">Experience</TabsTrigger>
            <TabsTrigger value="education">Education</TabsTrigger>
            <TabsTrigger value="skills">Skills</TabsTrigger>
            <TabsTrigger value="applications">Applications ({applications.length})</TabsTrigger>
          </TabsList>

          {/* Summary Tab */}
          <TabsContent value="summary">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                {parsedResume.summary && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Professional Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700">{parsedResume.summary}</p>
                    </CardContent>
                  </Card>
                )}

                {parsedResume.experience && parsedResume.experience.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Briefcase className="w-5 h-5 mr-2" />
                        Recent Experience
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {parsedResume.experience.slice(0, 2).map((exp, index) => (
                          <div key={index} className="border-l-2 border-indigo-200 pl-4">
                            <h3 className="font-semibold text-gray-900">{exp.title}</h3>
                            <p className="text-sm text-gray-600">{exp.company}</p>
                            <p className="text-xs text-gray-500 mt-1">
                              {exp.start_date} - {exp.end_date || 'Present'}
                            </p>
                            {exp.description && (
                              <p className="text-sm text-gray-700 mt-2">{exp.description}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              <div className="space-y-6">
                {parsedResume.skills && parsedResume.skills.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Award className="w-5 h-5 mr-2" />
                        Top Skills
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {parsedResume.skills.map((skill, index) => (
                          <Badge key={index} variant="secondary">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {parsedResume.certifications && parsedResume.certifications.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Award className="w-5 h-5 mr-2" />
                        Certifications
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {parsedResume.certifications.map((cert, index) => (
                          <div key={index} className="text-sm">
                            <p className="font-medium text-gray-900">{cert.name}</p>
                            <p className="text-gray-600">{cert.issuer}</p>
                            {cert.date && (
                              <p className="text-xs text-gray-500">{cert.date}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Experience Tab */}
          <TabsContent value="experience">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Briefcase className="w-5 h-5 mr-2" />
                  Work Experience
                </CardTitle>
              </CardHeader>
              <CardContent>
                {parsedResume.experience && parsedResume.experience.length > 0 ? (
                  <div className="space-y-6">
                    {parsedResume.experience.map((exp, index) => (
                      <div key={index} className="border-l-2 border-indigo-200 pl-4 pb-6 last:pb-0">
                        <h3 className="text-xl font-semibold text-gray-900">{exp.title}</h3>
                        <p className="text-gray-600 font-medium">{exp.company}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          {exp.start_date} - {exp.end_date || 'Present'}
                        </p>
                        {exp.description && (
                          <p className="text-gray-700 mt-3">{exp.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No experience information available</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Education Tab */}
          <TabsContent value="education">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <GraduationCap className="w-5 h-5 mr-2" />
                  Education
                </CardTitle>
              </CardHeader>
              <CardContent>
                {parsedResume.education && parsedResume.education.length > 0 ? (
                  <div className="space-y-6">
                    {parsedResume.education.map((edu, index) => (
                      <div key={index} className="border-l-2 border-indigo-200 pl-4">
                        <h3 className="text-xl font-semibold text-gray-900">{edu.degree}</h3>
                        <p className="text-gray-600 font-medium">{edu.institution}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          {edu.graduation_year || edu.year}
                        </p>
                        {edu.field && (
                          <p className="text-gray-700 mt-2">Field: {edu.field}</p>
                        )}
                        {edu.gpa && (
                          <p className="text-gray-700">GPA: {edu.gpa}</p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No education information available</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Skills Tab */}
          <TabsContent value="skills">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Award className="w-5 h-5 mr-2" />
                  Skills & Expertise
                </CardTitle>
              </CardHeader>
              <CardContent>
                {parsedResume.skills && parsedResume.skills.length > 0 ? (
                  <div className="flex flex-wrap gap-3">
                    {parsedResume.skills.map((skill, index) => (
                      <Badge key={index} variant="secondary" className="text-base px-4 py-2">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No skills information available</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Applications Tab */}
          <TabsContent value="applications">
            <div className="space-y-4">
              {applications.length > 0 ? (
                applications.map((app) => (
                  <Card 
                    key={app.id} 
                    className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => navigate(`/applications/${app.id}`)}
                  >
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">{app.job_title}</h3>
                            <StatusBadge status={app.status} />
                          </div>
                          
                          <div className="flex items-center space-x-4 text-sm text-gray-600">
                            <div className="flex items-center">
                              <Calendar className="w-4 h-4 mr-1" />
                              Applied: {new Date(app.created_at).toLocaleDateString()}
                            </div>
                            {app.ai_evaluation && (
                              <div className="flex items-center">
                                <Award className="w-4 h-4 mr-1" />
                                Score: {app.ai_evaluation.overall_score}/100
                              </div>
                            )}
                          </div>

                          {app.ai_evaluation && app.ai_evaluation.summary && (
                            <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                              {app.ai_evaluation.summary}
                            </p>
                          )}
                        </div>

                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card>
                  <CardContent className="py-16 text-center">
                    <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">No Applications</h3>
                    <p className="text-gray-600">This candidate hasn't applied to any positions yet</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
};

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
    <Badge className={statusStyles[status] || 'bg-gray-100 text-gray-700'}>
      {status.replace('_', ' ').toUpperCase()}
    </Badge>
  );
};

export default CandidateDetailPage;
