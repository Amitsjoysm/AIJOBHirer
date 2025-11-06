import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import axios from 'axios';
import { Sparkles, ArrowLeft, Plus, X } from 'lucide-react';
import { toast } from 'sonner';

const CreateJobPage = () => {
  const { API_URL, getAuthHeaders } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [useAI, setUseAI] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    department: '',
    description: '',
    requirements: [],
    nice_to_have: [],
    job_type: 'full_time',
    location_type: 'remote',
    location: '',
    experience_level: 'intermediate',
    salary_min: '',
    salary_max: '',
    salary_currency: 'USD',
    use_ai_generation: false,
    ai_input: ''
  });
  const [currentRequirement, setCurrentRequirement] = useState('');
  const [currentNiceToHave, setCurrentNiceToHave] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const jobData = {
        ...formData,
        salary_min: formData.salary_min ? parseFloat(formData.salary_min) : null,
        salary_max: formData.salary_max ? parseFloat(formData.salary_max) : null,
        screening_questions: []
      };

      const response = await axios.post(`${API_URL}/jobs`, jobData, {
        headers: getAuthHeaders()
      });

      toast.success(useAI ? 'Job created! AI is generating content...' : 'Job created successfully!');
      navigate(`/jobs/${response.data.id}`);
    } catch (error) {
      console.error('Failed to create job:', error);
      toast.error(error.response?.data?.detail || 'Failed to create job');
    } finally {
      setLoading(false);
    }
  };

  const addRequirement = () => {
    if (currentRequirement.trim()) {
      setFormData({
        ...formData,
        requirements: [...formData.requirements, currentRequirement.trim()]
      });
      setCurrentRequirement('');
    }
  };

  const removeRequirement = (index) => {
    setFormData({
      ...formData,
      requirements: formData.requirements.filter((_, i) => i !== index)
    });
  };

  const addNiceToHave = () => {
    if (currentNiceToHave.trim()) {
      setFormData({
        ...formData,
        nice_to_have: [...formData.nice_to_have, currentNiceToHave.trim()]
      });
      setCurrentNiceToHave('');
    }
  };

  const removeNiceToHave = (index) => {
    setFormData({
      ...formData,
      nice_to_have: formData.nice_to_have.filter((_, i) => i !== index)
    });
  };

  return (
    <DashboardLayout>
      <div data-testid="create-job-page" className="max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/jobs')}
            className="mb-4"
            data-testid="back-btn"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Jobs
          </Button>
          <h1 className="text-3xl font-bold text-gray-900">Create Job Posting</h1>
          <p className="text-gray-600 mt-1">Fill in the details or let AI help you create a compelling job posting</p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* AI Toggle */}
          <Card className="mb-6 border-indigo-200 bg-indigo-50">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Sparkles className="w-6 h-6 text-indigo-600" />
                  <div>
                    <h3 className="font-semibold text-gray-900">AI-Powered Job Creation</h3>
                    <p className="text-sm text-gray-600">Let AI generate job description and screening questions</p>
                  </div>
                </div>
                <Switch
                  checked={useAI}
                  onCheckedChange={(checked) => {
                    setUseAI(checked);
                    setFormData({ ...formData, use_ai_generation: checked });
                  }}
                  data-testid="ai-toggle"
                />
              </div>
              
              {useAI && (
                <div className="mt-4">
                  <Label htmlFor="ai_input">Tell AI about this role</Label>
                  <Textarea
                    id="ai_input"
                    placeholder="E.g., We're looking for a senior React developer with 5+ years experience to lead our frontend team..."
                    value={formData.ai_input}
                    onChange={(e) => setFormData({ ...formData, ai_input: e.target.value })}
                    rows={3}
                    className="mt-2"
                    data-testid="ai-input"
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Basic Information */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="title">Job Title *</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                    placeholder="e.g., Senior Software Engineer"
                    data-testid="job-title-input"
                  />
                </div>
                <div>
                  <Label htmlFor="department">Department *</Label>
                  <Input
                    id="department"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    required
                    placeholder="e.g., Engineering"
                    data-testid="department-input"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="job_type">Job Type</Label>
                  <Select value={formData.job_type} onValueChange={(value) => setFormData({ ...formData, job_type: value })}>
                    <SelectTrigger data-testid="job-type-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="full_time">Full Time</SelectItem>
                      <SelectItem value="part_time">Part Time</SelectItem>
                      <SelectItem value="contract">Contract</SelectItem>
                      <SelectItem value="internship">Internship</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="experience_level">Experience Level</Label>
                  <Select value={formData.experience_level} onValueChange={(value) => setFormData({ ...formData, experience_level: value })}>
                    <SelectTrigger data-testid="experience-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="entry">Entry Level</SelectItem>
                      <SelectItem value="intermediate">Intermediate</SelectItem>
                      <SelectItem value="senior">Senior</SelectItem>
                      <SelectItem value="lead">Lead</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="location_type">Location Type</Label>
                  <Select value={formData.location_type} onValueChange={(value) => setFormData({ ...formData, location_type: value })}>
                    <SelectTrigger data-testid="location-type-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="remote">Remote</SelectItem>
                      <SelectItem value="hybrid">Hybrid</SelectItem>
                      <SelectItem value="onsite">On-site</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    placeholder="e.g., San Francisco, CA"
                    data-testid="location-input"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="description">Job Description {!useAI && '*'}</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required={!useAI}
                  rows={6}
                  placeholder="Describe the role, responsibilities, and what makes this opportunity exciting..."
                  data-testid="description-input"
                />
              </div>
            </CardContent>
          </Card>

          {/* Requirements */}
          {!useAI && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Requirements</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Required Qualifications</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      value={currentRequirement}
                      onChange={(e) => setCurrentRequirement(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addRequirement())}
                      placeholder="e.g., 5+ years of React experience"
                      data-testid="requirement-input"
                    />
                    <Button type="button" onClick={addRequirement} data-testid="add-requirement-btn">
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {formData.requirements.map((req, index) => (
                      <div key={index} className="flex items-center gap-2 bg-gray-100 px-3 py-1 rounded-full">
                        <span className="text-sm">{req}</span>
                        <button type="button" onClick={() => removeRequirement(index)}>
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <Label>Nice to Have</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      value={currentNiceToHave}
                      onChange={(e) => setCurrentNiceToHave(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addNiceToHave())}
                      placeholder="e.g., Experience with TypeScript"
                      data-testid="nicetohave-input"
                    />
                    <Button type="button" onClick={addNiceToHave} data-testid="add-nicetohave-btn">
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {formData.nice_to_have.map((item, index) => (
                      <div key={index} className="flex items-center gap-2 bg-indigo-50 px-3 py-1 rounded-full">
                        <span className="text-sm">{item}</span>
                        <button type="button" onClick={() => removeNiceToHave(index)}>
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Salary */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Compensation (Optional)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="salary_min">Minimum Salary</Label>
                  <Input
                    id="salary_min"
                    type="number"
                    value={formData.salary_min}
                    onChange={(e) => setFormData({ ...formData, salary_min: e.target.value })}
                    placeholder="50000"
                    data-testid="salary-min-input"
                  />
                </div>
                <div>
                  <Label htmlFor="salary_max">Maximum Salary</Label>
                  <Input
                    id="salary_max"
                    type="number"
                    value={formData.salary_max}
                    onChange={(e) => setFormData({ ...formData, salary_max: e.target.value })}
                    placeholder="80000"
                    data-testid="salary-max-input"
                  />
                </div>
                <div>
                  <Label htmlFor="salary_currency">Currency</Label>
                  <Select value={formData.salary_currency} onValueChange={(value) => setFormData({ ...formData, salary_currency: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="USD">USD</SelectItem>
                      <SelectItem value="EUR">EUR</SelectItem>
                      <SelectItem value="GBP">GBP</SelectItem>
                      <SelectItem value="INR">INR</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Submit */}
          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => navigate('/jobs')}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading} data-testid="submit-job-btn">
              {loading ? 'Creating...' : 'Create Job'}
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
};

export default CreateJobPage;
