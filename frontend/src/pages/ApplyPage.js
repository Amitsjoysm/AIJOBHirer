import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import axios from 'axios';
import { ArrowLeft, Upload, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const ApplyPage = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    candidate_name: '',
    candidate_email: '',
    candidate_phone: '',
    candidate_linkedin: '',
    resume_url: '',
    questionnaire_answers: []
  });
  const [resumeFile, setResumeFile] = useState(null);

  const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

  useEffect(() => {
    fetchJobDetails();
  }, [jobId]);

  const fetchJobDetails = async () => {
    try {
      const jobResponse = await axios.get(`${API_URL}/jobs/${jobId}`);
      setJob(jobResponse.data);

      // Fetch company
      const companyResponse = await axios.get(`${API_URL}/companies/slug/techcorp`);
      setCompany(companyResponse.data);

      // Initialize questionnaire answers
      if (jobResponse.data.screening_questions) {
        setFormData(prev => ({
          ...prev,
          questionnaire_answers: jobResponse.data.screening_questions.map(q => ({
            question: q.question,
            answer: ''
          }))
        }));
      }
    } catch (error) {
      console.error('Failed to fetch job:', error);
      toast.error('Job not found');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error('File size should not exceed 5MB');
        return;
      }
      if (!['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)) {
        toast.error('Only PDF and Word documents are allowed');
        return;
      }
      setResumeFile(file);
      // In production, upload to cloud storage and get URL
      setFormData({ ...formData, resume_url: `https://storage.example.com/resumes/${file.name}` });
    }
  };

  const handleQuestionnaireChange = (index, value) => {
    const updatedAnswers = [...formData.questionnaire_answers];
    updatedAnswers[index] = {
      ...updatedAnswers[index],
      answer: value
    };
    setFormData({ ...formData, questionnaire_answers: updatedAnswers });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!resumeFile) {
      toast.error('Please upload your resume');
      return;
    }

    setSubmitting(true);

    try {
      const applicationData = {
        ...formData,
        job_id: jobId
      };

      await axios.post(`${API_URL}/applications`, applicationData);
      setSubmitted(true);
      toast.success('Application submitted successfully!');
    } catch (error) {
      console.error('Failed to submit application:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit application');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Job not found</h1>
          <p className="text-gray-600">The job you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-6">
        <Card className="max-w-md w-full">
          <CardContent className="pt-12 pb-12 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Application Submitted!</h2>
            <p className="text-gray-600 mb-8">
              Thank you for applying to <span className="font-semibold">{job.title}</span> at {company?.name}.
              We'll review your application and get back to you soon.
            </p>
            <Button onClick={() => navigate(`/careers/${company?.slug}`)} data-testid="back-to-jobs-btn">
              View More Jobs
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-6" data-testid="apply-page">
      <div className="container mx-auto max-w-3xl">
        <Button 
          variant="ghost" 
          onClick={() => navigate(-1)}
          className="mb-6"
          data-testid="back-btn"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Apply for {job.title}</h1>
          <p className="text-gray-600">{company?.name} • {job.location_type}</p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Personal Information */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="candidate_name">Full Name *</Label>
                  <Input
                    id="candidate_name"
                    value={formData.candidate_name}
                    onChange={(e) => setFormData({ ...formData, candidate_name: e.target.value })}
                    required
                    placeholder="John Doe"
                    data-testid="name-input"
                  />
                </div>
                <div>
                  <Label htmlFor="candidate_email">Email *</Label>
                  <Input
                    id="candidate_email"
                    type="email"
                    value={formData.candidate_email}
                    onChange={(e) => setFormData({ ...formData, candidate_email: e.target.value })}
                    required
                    placeholder="john@example.com"
                    data-testid="email-input"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="candidate_phone">Phone</Label>
                  <Input
                    id="candidate_phone"
                    type="tel"
                    value={formData.candidate_phone}
                    onChange={(e) => setFormData({ ...formData, candidate_phone: e.target.value })}
                    placeholder="+1 (555) 123-4567"
                    data-testid="phone-input"
                  />
                </div>
                <div>
                  <Label htmlFor="candidate_linkedin">LinkedIn Profile</Label>
                  <Input
                    id="candidate_linkedin"
                    type="url"
                    value={formData.candidate_linkedin}
                    onChange={(e) => setFormData({ ...formData, candidate_linkedin: e.target.value })}
                    placeholder="https://linkedin.com/in/johndoe"
                    data-testid="linkedin-input"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Resume Upload */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Resume *</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-400 transition-colors">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <label htmlFor="resume" className="cursor-pointer">
                  <span className="text-indigo-600 hover:text-indigo-700 font-medium">
                    Click to upload
                  </span>
                  <span className="text-gray-600"> or drag and drop</span>
                  <p className="text-sm text-gray-500 mt-2">PDF or Word (Max 5MB)</p>
                </label>
                <input
                  id="resume"
                  type="file"
                  className="hidden"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                  data-testid="resume-input"
                />
                {resumeFile && (
                  <p className="mt-4 text-sm text-green-600 font-medium">
                    ✓ {resumeFile.name}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Screening Questions */}
          {formData.questionnaire_answers.length > 0 && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Screening Questions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {formData.questionnaire_answers.map((qa, index) => (
                  <div key={index}>
                    <Label htmlFor={`question-${index}`}>
                      {qa.question} {job.screening_questions[index]?.required && '*'}
                    </Label>
                    <Textarea
                      id={`question-${index}`}
                      value={qa.answer}
                      onChange={(e) => handleQuestionnaireChange(index, e.target.value)}
                      required={job.screening_questions[index]?.required}
                      rows={4}
                      placeholder="Your answer..."
                      className="mt-2"
                      data-testid={`question-${index}-input`}
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Submit */}
          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => navigate(-1)}>
              Cancel
            </Button>
            <Button type="submit" disabled={submitting} data-testid="submit-application-btn">
              {submitting ? 'Submitting...' : 'Submit Application'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ApplyPage;
