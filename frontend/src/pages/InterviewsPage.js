import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import axios from 'axios';
import { Calendar, Video, Phone, MapPin, Clock, User, Briefcase, Star, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';

const InterviewsPage = () => {
  const { API_URL, getAuthHeaders } = useAuth();
  const navigate = useNavigate();
  const [interviews, setInterviews] = useState([]);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('upcoming');
  const [showScheduleDialog, setShowScheduleDialog] = useState(false);
  const [showFeedbackDialog, setShowFeedbackDialog] = useState(false);
  const [selectedInterview, setSelectedInterview] = useState(null);
  const [scheduleForm, setScheduleForm] = useState({
    application_id: '',
    interview_type: 'video',
    scheduled_at: '',
    duration_minutes: 60,
    meeting_link: '',
    notes: ''
  });
  const [feedbackForm, setFeedbackForm] = useState({
    rating: 3,
    strengths: '',
    weaknesses: '',
    notes: '',
    recommendation: 'maybe'
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch all applications for the user's jobs
      const appsResponse = await axios.get(`${API_URL}/applications`, {
        headers: getAuthHeaders()
      });
      setApplications(appsResponse.data);

      // Fetch all interviews
      const interviewsData = [];
      for (const app of appsResponse.data) {
        try {
          const intResponse = await axios.get(
            `${API_URL}/interviews/application/${app.id}`,
            { headers: getAuthHeaders() }
          );
          interviewsData.push(...intResponse.data.map(i => ({ ...i, application: app })));
        } catch (err) {
          // Continue if no interviews found
        }
      }
      setInterviews(interviewsData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load interviews');
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleInterview = async (e) => {
    e.preventDefault();
    try {
      await axios.post(
        `${API_URL}/interviews`,
        {
          ...scheduleForm,
          interviewer_id: 'current_user' // This would be from auth context
        },
        { headers: getAuthHeaders() }
      );
      toast.success('Interview scheduled successfully!');
      setShowScheduleDialog(false);
      setScheduleForm({
        application_id: '',
        interview_type: 'video',
        scheduled_at: '',
        duration_minutes: 60,
        meeting_link: '',
        notes: ''
      });
      fetchData();
    } catch (error) {
      console.error('Failed to schedule interview:', error);
      toast.error(error.response?.data?.detail || 'Failed to schedule interview');
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    try {
      const strengthsList = feedbackForm.strengths.split('\n').filter(s => s.trim());
      const weaknessesList = feedbackForm.weaknesses.split('\n').filter(w => w.trim());
      
      await axios.patch(
        `${API_URL}/interviews/${selectedInterview.id}`,
        {
          status: 'completed',
          feedback: {
            rating: parseInt(feedbackForm.rating),
            strengths: strengthsList,
            weaknesses: weaknessesList,
            notes: feedbackForm.notes,
            recommendation: feedbackForm.recommendation
          }
        },
        { headers: getAuthHeaders() }
      );
      toast.success('Feedback submitted successfully!');
      setShowFeedbackDialog(false);
      setSelectedInterview(null);
      setFeedbackForm({
        rating: 3,
        strengths: '',
        weaknesses: '',
        notes: '',
        recommendation: 'maybe'
      });
      fetchData();
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      toast.error('Failed to submit feedback');
    }
  };

  const getInterviewsByStatus = (status) => {
    const now = new Date();
    return interviews.filter(interview => {
      const scheduledDate = new Date(interview.scheduled_at);
      if (status === 'upcoming') {
        return interview.status === 'scheduled' && scheduledDate >= now;
      } else if (status === 'past') {
        return interview.status === 'completed' || (interview.status === 'scheduled' && scheduledDate < now);
      }
      return interview.status === status;
    });
  };

  const getInterviewIcon = (type) => {
    switch (type) {
      case 'video': return <Video className="w-5 h-5" />;
      case 'phone': return <Phone className="w-5 h-5" />;
      case 'onsite': return <MapPin className="w-5 h-5" />;
      default: return <Calendar className="w-5 h-5" />;
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      scheduled: 'bg-blue-100 text-blue-700',
      completed: 'bg-green-100 text-green-700',
      cancelled: 'bg-red-100 text-red-700',
      rescheduled: 'bg-yellow-100 text-yellow-700'
    };
    return (
      <Badge className={variants[status]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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

  return (
    <DashboardLayout>
      <div data-testid="interviews-page">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Interviews</h1>
            <p className="text-gray-600 mt-1">Schedule and manage candidate interviews</p>
          </div>
          <Dialog open={showScheduleDialog} onOpenChange={setShowScheduleDialog}>
            <DialogTrigger asChild>
              <Button className="bg-indigo-600 hover:bg-indigo-700">
                <Calendar className="w-4 h-4 mr-2" />
                Schedule Interview
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Schedule New Interview</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleScheduleInterview} className="space-y-4">
                <div>
                  <Label>Select Application</Label>
                  <Select
                    value={scheduleForm.application_id}
                    onValueChange={(value) => setScheduleForm({ ...scheduleForm, application_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose candidate..." />
                    </SelectTrigger>
                    <SelectContent>
                      {applications.filter(a => a.status === 'shortlisted' || a.status === 'screening').map(app => (
                        <SelectItem key={app.id} value={app.id}>
                          {app.candidate_name} - {app.job_title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Interview Type</Label>
                    <Select
                      value={scheduleForm.interview_type}
                      onValueChange={(value) => setScheduleForm({ ...scheduleForm, interview_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="video">Video Call</SelectItem>
                        <SelectItem value="phone">Phone Call</SelectItem>
                        <SelectItem value="onsite">Onsite</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Duration (minutes)</Label>
                    <Input
                      type="number"
                      value={scheduleForm.duration_minutes}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, duration_minutes: parseInt(e.target.value) })}
                    />
                  </div>
                </div>

                <div>
                  <Label>Scheduled Date & Time</Label>
                  <Input
                    type="datetime-local"
                    value={scheduleForm.scheduled_at}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, scheduled_at: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <Label>Meeting Link (for video/phone)</Label>
                  <Input
                    type="url"
                    placeholder="https://zoom.us/j/..."
                    value={scheduleForm.meeting_link}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, meeting_link: e.target.value })}
                  />
                </div>

                <div>
                  <Label>Notes</Label>
                  <Textarea
                    placeholder="Additional notes for the interview..."
                    value={scheduleForm.notes}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, notes: e.target.value })}
                    rows={3}
                  />
                </div>

                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setShowScheduleDialog(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={!scheduleForm.application_id || !scheduleForm.scheduled_at}>
                    Schedule Interview
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Upcoming</p>
                  <p className="text-2xl font-bold">{getInterviewsByStatus('upcoming').length}</p>
                </div>
                <Calendar className="w-10 h-10 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Completed</p>
                  <p className="text-2xl font-bold">{interviews.filter(i => i.status === 'completed').length}</p>
                </div>
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Cancelled</p>
                  <p className="text-2xl font-bold">{interviews.filter(i => i.status === 'cancelled').length}</p>
                </div>
                <XCircle className="w-10 h-10 text-red-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total</p>
                  <p className="text-2xl font-bold">{interviews.length}</p>
                </div>
                <Briefcase className="w-10 h-10 text-indigo-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Interviews List */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="upcoming">Upcoming ({getInterviewsByStatus('upcoming').length})</TabsTrigger>
            <TabsTrigger value="past">Past ({getInterviewsByStatus('past').length})</TabsTrigger>
            <TabsTrigger value="all">All ({interviews.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="upcoming" className="mt-6">
            {getInterviewsByStatus('upcoming').length === 0 ? (
              <Card>
                <CardContent className="py-16 text-center">
                  <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No upcoming interviews</h3>
                  <p className="text-gray-600 mb-4">Schedule interviews with shortlisted candidates</p>
                  <Button onClick={() => setShowScheduleDialog(true)}>Schedule Interview</Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {getInterviewsByStatus('upcoming').map((interview) => (
                  <InterviewCard
                    key={interview.id}
                    interview={interview}
                    onViewApplication={() => navigate(`/applications/${interview.application_id}`)}
                    onAddFeedback={() => {
                      setSelectedInterview(interview);
                      setShowFeedbackDialog(true);
                    }}
                    getInterviewIcon={getInterviewIcon}
                    getStatusBadge={getStatusBadge}
                    formatDateTime={formatDateTime}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="past" className="mt-6">
            {getInterviewsByStatus('past').length === 0 ? (
              <Card>
                <CardContent className="py-16 text-center">
                  <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No past interviews</h3>
                  <p className="text-gray-600">Completed interviews will appear here</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {getInterviewsByStatus('past').map((interview) => (
                  <InterviewCard
                    key={interview.id}
                    interview={interview}
                    onViewApplication={() => navigate(`/applications/${interview.application_id}`)}
                    onAddFeedback={() => {
                      setSelectedInterview(interview);
                      setShowFeedbackDialog(true);
                    }}
                    getInterviewIcon={getInterviewIcon}
                    getStatusBadge={getStatusBadge}
                    formatDateTime={formatDateTime}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="all" className="mt-6">
            {interviews.length === 0 ? (
              <Card>
                <CardContent className="py-16 text-center">
                  <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No interviews scheduled</h3>
                  <p className="text-gray-600 mb-4">Start scheduling interviews with your candidates</p>
                  <Button onClick={() => setShowScheduleDialog(true)}>Schedule First Interview</Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {interviews.map((interview) => (
                  <InterviewCard
                    key={interview.id}
                    interview={interview}
                    onViewApplication={() => navigate(`/applications/${interview.application_id}`)}
                    onAddFeedback={() => {
                      setSelectedInterview(interview);
                      setShowFeedbackDialog(true);
                    }}
                    getInterviewIcon={getInterviewIcon}
                    getStatusBadge={getStatusBadge}
                    formatDateTime={formatDateTime}
                  />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Feedback Dialog */}
        <Dialog open={showFeedbackDialog} onOpenChange={setShowFeedbackDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Interview Feedback</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmitFeedback} className="space-y-4">
              <div>
                <Label>Rating (1-5)</Label>
                <Select
                  value={feedbackForm.rating.toString()}
                  onValueChange={(value) => setFeedbackForm({ ...feedbackForm, rating: parseInt(value) })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[1, 2, 3, 4, 5].map(r => (
                      <SelectItem key={r} value={r.toString()}>
                        {r} Star{r > 1 ? 's' : ''}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Strengths (one per line)</Label>
                <Textarea
                  placeholder="Good communication skills&#10;Strong technical knowledge&#10;..."
                  value={feedbackForm.strengths}
                  onChange={(e) => setFeedbackForm({ ...feedbackForm, strengths: e.target.value })}
                  rows={3}
                />
              </div>

              <div>
                <Label>Areas for Improvement (one per line)</Label>
                <Textarea
                  placeholder="Limited experience with React&#10;Needs improvement in system design&#10;..."
                  value={feedbackForm.weaknesses}
                  onChange={(e) => setFeedbackForm({ ...feedbackForm, weaknesses: e.target.value })}
                  rows={3}
                />
              </div>

              <div>
                <Label>Additional Notes</Label>
                <Textarea
                  placeholder="Overall impression and additional comments..."
                  value={feedbackForm.notes}
                  onChange={(e) => setFeedbackForm({ ...feedbackForm, notes: e.target.value })}
                  rows={3}
                  required
                />
              </div>

              <div>
                <Label>Recommendation</Label>
                <Select
                  value={feedbackForm.recommendation}
                  onValueChange={(value) => setFeedbackForm({ ...feedbackForm, recommendation: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="strong_hire">Strong Hire</SelectItem>
                    <SelectItem value="hire">Hire</SelectItem>
                    <SelectItem value="maybe">Maybe</SelectItem>
                    <SelectItem value="no_hire">No Hire</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setShowFeedbackDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit">Submit Feedback</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
};

// Interview Card Component
const InterviewCard = ({ interview, onViewApplication, onAddFeedback, getInterviewIcon, getStatusBadge, formatDateTime }) => {
  const application = interview.application;
  
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4 flex-1">
            <Avatar className="h-12 w-12">
              <AvatarFallback className="bg-indigo-100 text-indigo-600 font-semibold">
                {application?.candidate_name?.split(' ').map(n => n[0]).join('') || '?'}
              </AvatarFallback>
            </Avatar>
            
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <h3 className="font-semibold text-lg">{application?.candidate_name || 'Unknown'}</h3>
                {getStatusBadge(interview.status)}
              </div>
              <p className="text-sm text-gray-600 mb-2">{application?.job_title}</p>
              
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center">
                  {getInterviewIcon(interview.interview_type)}
                  <span className="ml-1 capitalize">{interview.interview_type}</span>
                </div>
                <div className="flex items-center">
                  <Calendar className="w-4 h-4 mr-1" />
                  {formatDateTime(interview.scheduled_at)}
                </div>
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  {interview.duration_minutes} min
                </div>
              </div>

              {interview.meeting_link && (
                <a
                  href={interview.meeting_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-indigo-600 hover:text-indigo-700 mt-2 inline-block"
                >
                  Join Meeting →
                </a>
              )}

              {interview.feedback && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Star className="w-4 h-4 text-yellow-500" />
                    <span className="text-sm font-medium">Rating: {interview.feedback.rating}/5</span>
                    <Badge className={
                      interview.feedback.recommendation === 'strong_hire' || interview.feedback.recommendation === 'hire'
                        ? 'bg-green-100 text-green-700'
                        : interview.feedback.recommendation === 'no_hire'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }>
                      {interview.feedback.recommendation.replace('_', ' ')}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">{interview.feedback.notes}</p>
                </div>
              )}
            </div>
          </div>

          <div className="flex space-x-2">
            <Button variant="outline" size="sm" onClick={onViewApplication}>
              View Application
            </Button>
            {interview.status === 'scheduled' && !interview.feedback && (
              <Button size="sm" onClick={onAddFeedback}>
                Add Feedback
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default InterviewsPage;
