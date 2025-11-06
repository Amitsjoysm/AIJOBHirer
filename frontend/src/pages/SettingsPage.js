import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { toast } from 'sonner';
import axios from 'axios';

const SettingsPage = () => {
  const { API_URL, getAuthHeaders, user } = useAuth();
  const [companyData, setCompanyData] = useState({
    name: '',
    slug: '',
    industry: '',
    website: '',
    description: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API_URL}/companies`, companyData, {
        headers: getAuthHeaders()
      });
      toast.success('Company profile created!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create company');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div data-testid="settings-page">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        <div className="max-w-2xl">
          <Card>
            <CardHeader>
              <CardTitle>Company Profile</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6" data-testid="company-form">
                <div>
                  <Label htmlFor="name">Company Name</Label>
                  <Input
                    id="name"
                    value={companyData.name}
                    onChange={(e) => setCompanyData({ ...companyData, name: e.target.value })}
                    required
                    data-testid="company-name-input"
                  />
                </div>

                <div>
                  <Label htmlFor="slug">Company Slug</Label>
                  <Input
                    id="slug"
                    value={companyData.slug}
                    onChange={(e) => setCompanyData({ ...companyData, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '') })}
                    placeholder="your-company"
                    required
                    data-testid="company-slug-input"
                  />
                  <p className="text-sm text-gray-500 mt-1">Your career page: hireflow.ai/{companyData.slug}</p>
                </div>

                <div>
                  <Label htmlFor="industry">Industry</Label>
                  <Input
                    id="industry"
                    value={companyData.industry}
                    onChange={(e) => setCompanyData({ ...companyData, industry: e.target.value })}
                    required
                    data-testid="company-industry-input"
                  />
                </div>

                <div>
                  <Label htmlFor="website">Website</Label>
                  <Input
                    id="website"
                    type="url"
                    value={companyData.website}
                    onChange={(e) => setCompanyData({ ...companyData, website: e.target.value })}
                    placeholder="https://your-company.com"
                    data-testid="company-website-input"
                  />
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <textarea
                    id="description"
                    className="w-full px-3 py-2 border rounded-lg"
                    rows={4}
                    value={companyData.description}
                    onChange={(e) => setCompanyData({ ...companyData, description: e.target.value })}
                    data-testid="company-description-input"
                  />
                </div>

                <Button type="submit" disabled={loading} data-testid="save-company-btn">
                  {loading ? 'Saving...' : 'Save Company Profile'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default SettingsPage;
