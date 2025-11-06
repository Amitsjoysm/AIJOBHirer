import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Card, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';
import axios from 'axios';
import { Search, Users, Mail, Linkedin } from 'lucide-react';
import { toast } from 'sonner';

const CandidatesPage = () => {
  const { API_URL, getAuthHeaders } = useAuth();
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await axios.get(`${API_URL}/candidates`, {
        headers: getAuthHeaders()
      });
      setCandidates(response.data);
    } catch (error) {
      console.error('Failed to fetch candidates:', error);
      toast.error('Failed to load candidates');
    } finally {
      setLoading(false);
    }
  };

  const filteredCandidates = candidates.filter(candidate =>
    candidate.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    candidate.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
      <div data-testid="candidates-page">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Candidates</h1>
          <p className="text-gray-600 mt-1">Browse and manage all candidates</p>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Input
              placeholder="Search candidates..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              data-testid="search-candidates-input"
            />
          </div>
        </div>

        {/* Candidates List */}
        {filteredCandidates.length === 0 ? (
          <Card>
            <CardContent className="py-16 text-center">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No candidates found</h3>
              <p className="text-gray-600">Candidates will appear here as they apply to your jobs</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCandidates.map((candidate) => (
              <Card 
                key={candidate.id} 
                className="hover:shadow-lg transition-shadow"
                data-testid={`candidate-${candidate.id}`}
              >
                <CardContent className="pt-6">
                  <div className="text-center mb-4">
                    <Avatar className="h-16 w-16 mx-auto mb-3">
                      <AvatarFallback className="bg-indigo-100 text-indigo-600 text-xl font-semibold">
                        {candidate.full_name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <h3 className="font-semibold text-gray-900 text-lg">{candidate.full_name}</h3>
                  </div>

                  <div className="space-y-2 text-sm">
                    <a 
                      href={`mailto:${candidate.email}`}
                      className="flex items-center text-gray-600 hover:text-indigo-600"
                    >
                      <Mail className="w-4 h-4 mr-2" />
                      {candidate.email}
                    </a>

                    {candidate.linkedin_url && (
                      <a 
                        href={candidate.linkedin_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center text-gray-600 hover:text-indigo-600"
                      >
                        <Linkedin className="w-4 h-4 mr-2" />
                        LinkedIn Profile
                      </a>
                    )}
                  </div>

                  {candidate.parsed_resume?.skills?.length > 0 && (
                    <div className="mt-4 pt-4 border-t">
                      <p className="text-xs text-gray-500 mb-2">Skills</p>
                      <div className="flex flex-wrap gap-1">
                        {candidate.parsed_resume.skills.slice(0, 5).map((skill, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                        {candidate.parsed_resume.skills.length > 5 && (
                          <Badge variant="secondary" className="text-xs">
                            +{candidate.parsed_resume.skills.length - 5}
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="mt-4 text-xs text-gray-500 text-center">
                    {candidate.application_ids?.length || 0} application(s)
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default CandidatesPage;
