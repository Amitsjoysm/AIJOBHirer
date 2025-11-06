import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';
import axios from 'axios';
import { ArrowLeft, Mail, Phone, Linkedin, FileText, Star, CheckCircle, XCircle, Calendar } from 'lucide-react';
import { toast } from 'sonner';

const ApplicationDetailsPage = () => {
  const { applicationId } = useParams();
  const { API_URL, getAuthHeaders } = useAuth();
  const navigate = useNavigate();
  const [application, setApplication] = useState(null);
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);

  useEffect(() => {
    fetchApplication();
  }, [applicationId]);

  const fetchApplication = async () => {
    try {
      const response = await axios.get(`${API_URL}/applications/${applicationId}`, {
        headers: getAuthHeaders()
      });
      setApplication(response.data);

      // Fetch candidate details
      const candidateResponse = await axios.get(`${API_URL}/candidates/${response.data.candidate_id}`, {
        headers: getAuthHeaders()
      });
      setCandidate(candidateResponse.data);
    } catch (error) {
      console.error('Failed to fetch application:', error);
      toast.error('Failed to load application');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    setUpdatingStatus(true);
    try {
      await axios.patch(
        `${API_URL}/applications/${applicationId}/status`,
        { status: newStatus, notes: notes || undefined },
        { headers: getAuthHeaders() }
      );
      toast.success('Status updated successfully');
      setNotes('');
      fetchApplication();
    } catch (error) {
      toast.error('Failed to update status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      submitted: 'bg-blue-100 text-blue-700',
      screening: 'bg-yellow-100 text-yellow-700',
      shortlisted: 'bg-green-100 text-green-700',
      interview_scheduled: 'bg-purple-100 text-purple-700',
      offer: 'bg-emerald-100 text-emerald-700',
      rejected: 'bg-red-100 text-red-700'
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

  if (!application) {
    return (
      <DashboardLayout>
        <div className="text-center py-16">
          <p className="text-gray-600">Application not found</p>
        </div>
      </DashboardLayout>
    );
  }

  const evaluation = application.ai_evaluation;
  const parsedResume = candidate?.parsed_resume;

  return (
    <DashboardLayout>
      <div data-testid="application-details-page" className="max-w-6xl">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/applications')}
          className="mb-6"
          data-testid="back-btn"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Applications
        </Button>

        <div className="grid grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="col-span-2 space-y-6">
            {/* Candidate Info */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center space-x-4">
                    <Avatar className="h-16 w-16">
                      <AvatarFallback className="bg-indigo-100 text-indigo-600 text-xl font-semibold">
                        {application.candidate_name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <h2 className="text-2xl font-bold text-gray-900">{application.candidate_name}</h2>
                        {evaluation?.recommendation === 'strong_match' && (
                          <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        {application.candidate_email && (
                          <a href={`mailto:${application.candidate_email}`} className="flex items-center hover:text-indigo-600">
                            <Mail className="w-4 h-4 mr-1" />
                            {application.candidate_email}
                          </a>
                        )}
                        {application.candidate_phone && (
                          <span className="flex items-center">
                            <Phone className="w-4 h-4 mr-1" />
                            {application.candidate_phone}
                          </span>
                        )}
                        {application.candidate_linkedin && (
                          <a href={application.candidate_linkedin} target="_blank" rel="noopener noreferrer" className="flex items-center hover:text-indigo-600">
                            <Linkedin className="w-4 h-4 mr-1" />
                            LinkedIn
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                  <Badge className={getStatusColor(application.status)}>
                    {application.status.replace('_', ' ')}
                  </Badge>
                </div>

                <div className="text-sm text-gray-600">
                  Applied {new Date(application.created_at).toLocaleDateString()}
                </div>
              </CardContent>
            </Card>

            {/* AI Evaluation */}
            {evaluation && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="w-5 h-5 text-indigo-600" />
                    AI Evaluation
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-5 gap-4">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-indigo-600">
                        {Math.round(evaluation.overall_score)}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">Overall</div>
                    </div>
                    {evaluation.score_breakdown && Object.entries(evaluation.score_breakdown).map(([key, value]) => (
                      <div key={key} className="text-center">
                        <div className="text-2xl font-bold text-gray-700">
                          {Math.round(value)}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {key.replace('_', ' ').split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="pt-4 border-t">
                    <p className="text-gray-700">{evaluation.summary}</p>
                  </div>

                  {evaluation.strengths?.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        Strengths
                      </h4>
                      <ul className="list-disc list-inside space-y-1">
                        {evaluation.strengths.map((strength, index) => (
                          <li key={index} className="text-sm text-gray-600">{strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {evaluation.concerns?.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                        <XCircle className="w-4 h-4 text-red-600" />
                        Concerns
                      </h4>
                      <ul className="list-disc list-inside space-y-1">
                        {evaluation.concerns.map((concern, index) => (
                          <li key={index} className="text-sm text-gray-600">{concern}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Resume Summary */}
            {parsedResume && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-indigo-600" />
                    Resume Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {parsedResume.summary && (
                    <p className="text-gray-700">{parsedResume.summary}</p>
                  )}

                  {parsedResume.work_experience?.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Experience</h4>
                      <div className="space-y-3">
                        {parsedResume.work_experience.map((exp, index) => (
                          <div key={index} className="border-l-2 border-indigo-200 pl-4">
                            <h5 className="font-medium text-gray-900">{exp.title}</h5>
                            <p className="text-sm text-gray-600">{exp.company}</p>
                            <p className="text-xs text-gray-500">
                              {exp.start_date} - {exp.is_current ? 'Present' : exp.end_date}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {parsedResume.education?.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Education</h4>
                      <div className="space-y-2">
                        {parsedResume.education.map((edu, index) => (
                          <div key={index}>
                            <p className="font-medium text-gray-900">{edu.degree} in {edu.field_of_study}</p>
                            <p className="text-sm text-gray-600">{edu.institution}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {parsedResume.skills?.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {parsedResume.skills.map((skill, index) => (
                          <Badge key={index} variant="secondary">{skill}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Questionnaire Answers */}
            {application.questionnaire_answers?.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Screening Questions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {application.questionnaire_answers.map((qa, index) => (
                    <div key={index}>
                      <h4 className="font-medium text-gray-900 mb-1">{qa.question}</h4>
                      <p className="text-gray-600">{qa.answer}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar - Actions */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">Update Status</label>
                  <Select 
                    value={application.status}
                    onValueChange={handleStatusUpdate}
                    disabled={updatingStatus}
                  >
                    <SelectTrigger data-testid="status-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
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

                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">Add Notes</label>
                  <Textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add internal notes about this candidate..."
                    rows={4}
                    data-testid="notes-input"
                  />
                  <Button 
                    className="w-full mt-2" 
                    onClick={() => handleStatusUpdate(application.status)}
                    disabled={!notes || updatingStatus}
                    data-testid="save-notes-btn"
                  >
                    Save Notes
                  </Button>
                </div>

                <div className="pt-4 border-t space-y-2">
                  <Button 
                    className="w-full" 
                    variant="outline"
                    onClick={() => handleStatusUpdate('interview_scheduled')}
                    disabled={updatingStatus || application.status === 'interview_scheduled'}
                    data-testid="schedule-interview-btn"
                  >
                    <Calendar className="w-4 h-4 mr-2" />
                    Schedule Interview
                  </Button>
                  
                  <Button 
                    className="w-full" 
                    onClick={() => handleStatusUpdate('shortlisted')}
                    disabled={updatingStatus || application.status === 'shortlisted'}
                    data-testid="shortlist-btn"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Shortlist
                  </Button>
                  
                  <Button 
                    className="w-full" 
                    variant="destructive"
                    onClick={() => handleStatusUpdate('rejected')}
                    disabled={updatingStatus || application.status === 'rejected'}
                    data-testid="reject-btn"
                  >
                    <XCircle className="w-4 h-4 mr-2" />
                    Reject
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Activity Timeline */}
            {application.notes?.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {application.notes.map((note, index) => (
                      <div key={index} className="text-sm">
                        <p className="text-gray-700">{note.text}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(note.created_at).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ApplicationDetailsPage;
