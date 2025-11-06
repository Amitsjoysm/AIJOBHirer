import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { toast } from 'sonner';
import axios from 'axios';
import { 
  Building2, 
  Mail, 
  Link2, 
  CheckCircle2, 
  XCircle, 
  Loader2,
  Send,
  Calendar,
  Shield
} from 'lucide-react';

const EnhancedSettingsPage = () => {
  const { API_URL, getAuthHeaders, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [oauthStatus, setOauthStatus] = useState({
    google: false,
    microsoft: false
  });
  
  // Company profile state
  const [companyData, setCompanyData] = useState({
    name: '',
    slug: '',
    industry: '',
    website: '',
    description: ''
  });

  // Email configuration state
  const [emailConfig, setEmailConfig] = useState({
    provider: 'gmail',
    from_email: '',
    from_name: '',
    signature: ''
  });

  // SMTP config state
  const [smtpConfig, setSmtpConfig] = useState({
    host: '',
    port: 587,
    username: '',
    password: '',
    use_tls: true
  });

  const [emailConfigExists, setEmailConfigExists] = useState(false);
  const [testingEmail, setTestingEmail] = useState(false);

  useEffect(() => {
    fetchOAuthStatus();
    fetchEmailConfig();
    fetchCompanyProfile();
  }, []);

  const fetchOAuthStatus = () => {
    // Check OAuth connection status from user object
    if (user) {
      setOauthStatus({
        google: user.oauth_connected && user.google_credentials !== null,
        microsoft: user.oauth_connected && user.microsoft_credentials !== null
      });
    }
  };

  const fetchEmailConfig = async () => {
    try {
      const response = await axios.get(`${API_URL}/email-config`, {
        headers: getAuthHeaders()
      });
      
      if (response.data) {
        setEmailConfig({
          provider: response.data.provider,
          from_email: response.data.from_email,
          from_name: response.data.from_name || '',
          signature: response.data.signature || ''
        });
        setEmailConfigExists(true);
      }
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Failed to fetch email config:', error);
      }
    }
  };

  const fetchCompanyProfile = async () => {
    try {
      const response = await axios.get(`${API_URL}/companies/me`, {
        headers: getAuthHeaders()
      });
      
      if (response.data) {
        setCompanyData(response.data);
      }
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Failed to fetch company:', error);
      }
    }
  };

  const handleCompanySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API_URL}/companies`, companyData, {
        headers: getAuthHeaders()
      });
      toast.success('Company profile saved!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save company profile');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectGoogle = async () => {
    try {
      const response = await axios.get(`${API_URL}/oauth/google/url`, {
        headers: getAuthHeaders()
      });
      window.location.href = response.data.auth_url;
    } catch (error) {
      toast.error('Failed to start Google connection');
    }
  };

  const handleConnectMicrosoft = async () => {
    try {
      const response = await axios.get(`${API_URL}/oauth/microsoft/url`, {
        headers: getAuthHeaders()
      });
      window.location.href = response.data.auth_url;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to start Microsoft connection');
    }
  };

  const handleDisconnectOAuth = async (provider) => {
    try {
      await axios.post(`${API_URL}/oauth/disconnect/${provider}`, {}, {
        headers: getAuthHeaders()
      });
      toast.success(`${provider.charAt(0).toUpperCase() + provider.slice(1)} disconnected`);
      setOauthStatus({ ...oauthStatus, [provider]: false });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to disconnect');
    }
  };

  const handleEmailConfigSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...emailConfig,
        smtp_config: emailConfig.provider === 'smtp' ? smtpConfig : undefined
      };

      await axios.post(`${API_URL}/email-config`, payload, {
        headers: getAuthHeaders()
      });
      
      toast.success('Email configuration saved!');
      setEmailConfigExists(true);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save email configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleTestEmail = async () => {
    setTestingEmail(true);
    try {
      const response = await axios.post(`${API_URL}/email-config/test`, {}, {
        headers: getAuthHeaders()
      });
      
      if (response.data.success) {
        toast.success('Test email sent! Check your inbox.');
      } else {
        toast.error(response.data.message || 'Test failed');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send test email');
    } finally {
      setTestingEmail(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-600 mb-8">Manage your account, company profile, and integrations</p>

        <Tabs defaultValue="company" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="company" className="flex items-center gap-2">
              <Building2 className="w-4 h-4" />
              Company
            </TabsTrigger>
            <TabsTrigger value="integrations" className="flex items-center gap-2">
              <Link2 className="w-4 h-4" />
              Integrations
            </TabsTrigger>
            <TabsTrigger value="email" className="flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Email
            </TabsTrigger>
          </TabsList>

          {/* Company Profile Tab */}
          <TabsContent value="company">
            <Card>
              <CardHeader>
                <CardTitle>Company Profile</CardTitle>
                <CardDescription>
                  Set up your company information for your career page
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCompanySubmit} className="space-y-6">
                  <div>
                    <Label htmlFor="name">Company Name *</Label>
                    <Input
                      id="name"
                      value={companyData.name}
                      onChange={(e) => setCompanyData({ ...companyData, name: e.target.value })}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="slug">Company Slug *</Label>
                    <Input
                      id="slug"
                      value={companyData.slug}
                      onChange={(e) => setCompanyData({ ...companyData, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '') })}
                      placeholder="your-company"
                      required
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      Career page: {window.location.origin}/careers/{companyData.slug || 'your-company'}
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="industry">Industry *</Label>
                    <Input
                      id="industry"
                      value={companyData.industry}
                      onChange={(e) => setCompanyData({ ...companyData, industry: e.target.value })}
                      required
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
                    />
                  </div>

                  <div>
                    <Label htmlFor="description">Description</Label>
                    <textarea
                      id="description"
                      className="w-full px-3 py-2 border rounded-lg min-h-[100px]"
                      value={companyData.description}
                      onChange={(e) => setCompanyData({ ...companyData, description: e.target.value })}
                      placeholder="Tell candidates about your company..."
                    />
                  </div>

                  <Button type="submit" disabled={loading}>
                    {loading ? 'Saving...' : 'Save Company Profile'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Integrations Tab */}
          <TabsContent value="integrations">
            <div className="space-y-6">
              {/* Google Integration */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <Mail className="w-5 h-5" />
                        Google Integration
                      </CardTitle>
                      <CardDescription>
                        Connect Google for Gmail and Calendar access
                      </CardDescription>
                    </div>
                    {oauthStatus.google ? (
                      <CheckCircle2 className="w-6 h-6 text-green-600" />
                    ) : (
                      <XCircle className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-2">Permissions:</p>
                      <ul className="text-sm text-gray-600 space-y-1 ml-4">
                        <li>• Send emails via Gmail</li>
                        <li>• Create and manage calendar events</li>
                        <li>• Access your profile information</li>
                      </ul>
                    </div>
                    
                    {oauthStatus.google ? (
                      <div className="flex gap-2">
                        <Button variant="outline" disabled className="flex-1">
                          <CheckCircle2 className="w-4 h-4 mr-2" />
                          Connected
                        </Button>
                        <Button 
                          variant="destructive" 
                          onClick={() => handleDisconnectOAuth('google')}
                        >
                          Disconnect
                        </Button>
                      </div>
                    ) : (
                      <Button onClick={handleConnectGoogle} className="w-full">
                        Connect Google Account
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Microsoft Integration */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <Calendar className="w-5 h-5" />
                        Microsoft Integration
                      </CardTitle>
                      <CardDescription>
                        Connect Microsoft for Outlook and Calendar access
                      </CardDescription>
                    </div>
                    {oauthStatus.microsoft ? (
                      <CheckCircle2 className="w-6 h-6 text-green-600" />
                    ) : (
                      <XCircle className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-2">Permissions:</p>
                      <ul className="text-sm text-gray-600 space-y-1 ml-4">
                        <li>• Send emails via Outlook</li>
                        <li>• Create and manage calendar events</li>
                        <li>• Access your profile information</li>
                      </ul>
                    </div>
                    
                    {oauthStatus.microsoft ? (
                      <div className="flex gap-2">
                        <Button variant="outline" disabled className="flex-1">
                          <CheckCircle2 className="w-4 h-4 mr-2" />
                          Connected
                        </Button>
                        <Button 
                          variant="destructive" 
                          onClick={() => handleDisconnectOAuth('microsoft')}
                        >
                          Disconnect
                        </Button>
                      </div>
                    ) : (
                      <Button onClick={handleConnectMicrosoft} className="w-full">
                        Connect Microsoft Account
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Email Configuration Tab */}
          <TabsContent value="email">
            <Card>
              <CardHeader>
                <CardTitle>Email Configuration</CardTitle>
                <CardDescription>
                  Configure how HireFlow sends emails to candidates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleEmailConfigSubmit} className="space-y-6">
                  <div>
                    <Label htmlFor="provider">Email Provider *</Label>
                    <Select 
                      value={emailConfig.provider} 
                      onValueChange={(value) => setEmailConfig({ ...emailConfig, provider: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="gmail">
                          Gmail (via Google OAuth)
                        </SelectItem>
                        <SelectItem value="outlook">
                          Outlook (via Microsoft OAuth)
                        </SelectItem>
                        <SelectItem value="smtp">
                          Custom SMTP Server
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    
                    {emailConfig.provider === 'gmail' && !oauthStatus.google && (
                      <p className="text-sm text-amber-600 mt-2">
                        ⚠️ Please connect your Google account in the Integrations tab first
                      </p>
                    )}
                    
                    {emailConfig.provider === 'outlook' && !oauthStatus.microsoft && (
                      <p className="text-sm text-amber-600 mt-2">
                        ⚠️ Please connect your Microsoft account in the Integrations tab first
                      </p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="from_email">From Email *</Label>
                    <Input
                      id="from_email"
                      type="email"
                      value={emailConfig.from_email}
                      onChange={(e) => setEmailConfig({ ...emailConfig, from_email: e.target.value })}
                      placeholder="hr@yourcompany.com"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="from_name">From Name</Label>
                    <Input
                      id="from_name"
                      value={emailConfig.from_name}
                      onChange={(e) => setEmailConfig({ ...emailConfig, from_name: e.target.value })}
                      placeholder="HR Team"
                    />
                  </div>

                  {/* SMTP Configuration */}
                  {emailConfig.provider === 'smtp' && (
                    <div className="border rounded-lg p-4 space-y-4 bg-gray-50">
                      <h3 className="font-semibold text-sm">SMTP Server Settings</h3>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="smtp_host">SMTP Host *</Label>
                          <Input
                            id="smtp_host"
                            value={smtpConfig.host}
                            onChange={(e) => setSmtpConfig({ ...smtpConfig, host: e.target.value })}
                            placeholder="smtp.gmail.com"
                            required
                          />
                        </div>
                        
                        <div>
                          <Label htmlFor="smtp_port">Port *</Label>
                          <Input
                            id="smtp_port"
                            type="number"
                            value={smtpConfig.port}
                            onChange={(e) => setSmtpConfig({ ...smtpConfig, port: parseInt(e.target.value) })}
                            required
                          />
                        </div>
                      </div>

                      <div>
                        <Label htmlFor="smtp_username">Username *</Label>
                        <Input
                          id="smtp_username"
                          value={smtpConfig.username}
                          onChange={(e) => setSmtpConfig({ ...smtpConfig, username: e.target.value })}
                          placeholder="your@email.com"
                          required
                        />
                      </div>

                      <div>
                        <Label htmlFor="smtp_password">Password / App Password *</Label>
                        <Input
                          id="smtp_password"
                          type="password"
                          value={smtpConfig.password}
                          onChange={(e) => setSmtpConfig({ ...smtpConfig, password: e.target.value })}
                          placeholder="••••••••"
                          required
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Use app-specific password for Gmail/Outlook
                        </p>
                      </div>
                    </div>
                  )}

                  <div>
                    <Label htmlFor="signature">Email Signature (HTML)</Label>
                    <textarea
                      id="signature"
                      className="w-full px-3 py-2 border rounded-lg min-h-[100px] font-mono text-sm"
                      value={emailConfig.signature}
                      onChange={(e) => setEmailConfig({ ...emailConfig, signature: e.target.value })}
                      placeholder="<p>Best regards,<br>HR Team</p>"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      HTML signature appended to all emails
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <Button type="submit" disabled={loading} className="flex-1">
                      {loading ? 'Saving...' : 'Save Email Configuration'}
                    </Button>
                    
                    {emailConfigExists && (
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={handleTestEmail}
                        disabled={testingEmail}
                      >
                        {testingEmail ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Testing...
                          </>
                        ) : (
                          <>
                            <Send className="w-4 h-4 mr-2" />
                            Test Email
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
};

export default EnhancedSettingsPage;
