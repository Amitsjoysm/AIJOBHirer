"""OAuth service for Google and Microsoft authentication"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import msal
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class OAuthService:
    """Service for handling OAuth flows for Google and Microsoft"""
    
    # OAuth scopes
    GOOGLE_SCOPES = [
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/calendar'
    ]
    
    MICROSOFT_SCOPES = [
        'User.Read',
        'Mail.Send',
        'Calendars.ReadWrite',
        'offline_access'
    ]
    
    @staticmethod
    def get_google_oauth_url(redirect_uri: str, state: str) -> str:
        """Generate Google OAuth authorization URL"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
                        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=OAuthService.GOOGLE_SCOPES
            )
            flow.redirect_uri = redirect_uri
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state,
                prompt='consent'
            )
            
            logger.info(f"Generated Google OAuth URL with redirect: {redirect_uri}")
            return authorization_url
            
        except Exception as e:
            logger.error(f"Failed to generate Google OAuth URL: {str(e)}")
            raise
    
    @staticmethod
    async def exchange_google_code(code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange Google authorization code for tokens and user info"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
                        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=OAuthService.GOOGLE_SCOPES
            )
            flow.redirect_uri = redirect_uri
            
            # Exchange code for tokens
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Get user info
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            
            return {
                'user_info': {
                    'email': user_info['email'],
                    'full_name': user_info.get('name', ''),
                    'picture': user_info.get('picture', ''),
                    'email_verified': user_info.get('verified_email', False)
                },
                'credentials': {
                    'token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'scopes': credentials.scopes
                }
            }
            
        except Exception as e:
            logger.error(f"Google code exchange failed: {str(e)}")
            raise
    
    @staticmethod
    def get_microsoft_oauth_url(redirect_uri: str, state: str) -> str:
        """Generate Microsoft OAuth authorization URL"""
        try:
            client_id = os.environ.get('MICROSOFT_CLIENT_ID')
            tenant_id = os.environ.get('MICROSOFT_TENANT_ID', 'common')
            
            msal_app = msal.ConfidentialClientApplication(
                client_id,
                authority=f"https://login.microsoftonline.com/{tenant_id}",
                client_credential=os.environ.get('MICROSOFT_CLIENT_SECRET')
            )
            
            auth_url = msal_app.get_authorization_request_url(
                OAuthService.MICROSOFT_SCOPES,
                state=state,
                redirect_uri=redirect_uri
            )
            
            logger.info(f"Generated Microsoft OAuth URL with redirect: {redirect_uri}")
            return auth_url
            
        except Exception as e:
            logger.error(f"Failed to generate Microsoft OAuth URL: {str(e)}")
            raise
    
    @staticmethod
    async def exchange_microsoft_code(code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange Microsoft authorization code for tokens and user info"""
        try:
            client_id = os.environ.get('MICROSOFT_CLIENT_ID')
            tenant_id = os.environ.get('MICROSOFT_TENANT_ID', 'common')
            
            msal_app = msal.ConfidentialClientApplication(
                client_id,
                authority=f"https://login.microsoftonline.com/{tenant_id}",
                client_credential=os.environ.get('MICROSOFT_CLIENT_SECRET')
            )
            
            # Exchange code for tokens
            result = msal_app.acquire_token_by_authorization_code(
                code,
                scopes=OAuthService.MICROSOFT_SCOPES,
                redirect_uri=redirect_uri
            )
            
            if 'error' in result:
                raise Exception(result['error_description'])
            
            # Get user info from Microsoft Graph
            import requests
            headers = {'Authorization': f'Bearer {result["access_token"]}'}
            response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
            user_info = response.json()
            
            return {
                'user_info': {
                    'email': user_info['mail'] or user_info['userPrincipalName'],
                    'full_name': user_info.get('displayName', ''),
                    'email_verified': True
                },
                'credentials': {
                    'access_token': result['access_token'],
                    'refresh_token': result.get('refresh_token'),
                    'expires_in': result.get('expires_in'),
                    'scope': result.get('scope', '').split(' ')
                }
            }
            
        except Exception as e:
            logger.error(f"Microsoft code exchange failed: {str(e)}")
            raise
    
    @staticmethod
    async def refresh_google_token(refresh_token: str) -> Dict[str, Any]:
        """Refresh Google access token"""
        try:
            import requests
            
            data = {
                'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
                'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post('https://oauth2.googleapis.com/token', data=data)
            return response.json()
            
        except Exception as e:
            logger.error(f"Google token refresh failed: {str(e)}")
            raise
    
    @staticmethod
    async def refresh_microsoft_token(refresh_token: str) -> Dict[str, Any]:
        """Refresh Microsoft access token"""
        try:
            client_id = os.environ.get('MICROSOFT_CLIENT_ID')
            tenant_id = os.environ.get('MICROSOFT_TENANT_ID', 'common')
            
            msal_app = msal.ConfidentialClientApplication(
                client_id,
                authority=f"https://login.microsoftonline.com/{tenant_id}",
                client_credential=os.environ.get('MICROSOFT_CLIENT_SECRET')
            )
            
            result = msal_app.acquire_token_by_refresh_token(
                refresh_token,
                scopes=OAuthService.MICROSOFT_SCOPES
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Microsoft token refresh failed: {str(e)}")
            raise
