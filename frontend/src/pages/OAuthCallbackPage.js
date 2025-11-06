import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';
import { Sparkles } from 'lucide-react';

const OAuthCallbackPage = ({ provider }) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { API_URL, login: authLogin } = useAuth();
  const [status, setStatus] = useState('processing');

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');

      if (error) {
        toast.error(`OAuth failed: ${error}`);
        setStatus('error');
        setTimeout(() => navigate('/login'), 2000);
        return;
      }

      if (!code) {
        toast.error('No authorization code received');
        setStatus('error');
        setTimeout(() => navigate('/login'), 2000);
        return;
      }

      try {
        setStatus('processing');
        
        // Exchange code for tokens
        const response = await axios.post(
          `${API_URL}/oauth/${provider}/callback`,
          {
            code,
            state,
            redirect_uri: window.location.origin + `/auth/${provider}/callback`
          }
        );

        const { access_token, refresh_token } = response.data;
        
        // Store tokens
        localStorage.setItem('token', access_token);
        localStorage.setItem('refreshToken', refresh_token);
        
        // Fetch user data
        const userResponse = await axios.get(`${API_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${access_token}` }
        });
        
        localStorage.setItem('user', JSON.stringify(userResponse.data));
        
        setStatus('success');
        toast.success(`Successfully signed in with ${provider.charAt(0).toUpperCase() + provider.slice(1)}!`);
        
        setTimeout(() => navigate('/dashboard'), 1000);
      } catch (error) {
        console.error('OAuth callback error:', error);
        setStatus('error');
        toast.error(error.response?.data?.detail || 'Authentication failed');
        setTimeout(() => navigate('/login'), 2000);
      }
    };

    handleCallback();
  }, [searchParams, navigate, API_URL, provider]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-6">
      <div className="text-center">
        <div className="flex justify-center mb-6">
          <Sparkles className="w-16 h-16 text-indigo-600 animate-pulse" />
        </div>
        
        {status === 'processing' && (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Completing sign in...
            </h2>
            <p className="text-gray-600">
              Please wait while we set up your account
            </p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Success!
            </h2>
            <p className="text-gray-600">
              Redirecting to your dashboard...
            </p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Authentication Failed
            </h2>
            <p className="text-gray-600">
              Redirecting back to login...
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export const GoogleCallbackPage = () => <OAuthCallbackPage provider="google" />;
export const MicrosoftCallbackPage = () => <OAuthCallbackPage provider="microsoft" />;

export default OAuthCallbackPage;
