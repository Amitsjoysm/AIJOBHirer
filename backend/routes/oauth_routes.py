"""OAuth routes for Google and Microsoft authentication"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient
from services.oauth_service import OAuthService
from services.auth_service import AuthService
from services.database_service import DatabaseService
from models.user import Token, AuthProvider
from routes.auth_routes import get_current_user
import os
import uuid
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Get database
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)

@router.get("/google/url")
async def get_google_oauth_url(
    redirect_uri: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get Google OAuth authorization URL
    
    If user is authenticated, connects Google to existing account.
    If not authenticated, creates new account after OAuth.
    """
    try:
        # Use provided redirect_uri or construct from frontend URL
        if not redirect_uri:
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            redirect_uri = f"{frontend_url}/auth/google/callback"
        
        # State contains user_id if connecting to existing account
        state = current_user['id'] if current_user else 'new_user'
        
        auth_url = OAuthService.get_google_oauth_url(redirect_uri, state)
        
        return {
            "auth_url": auth_url,
            "redirect_uri": redirect_uri,
            "info": "Add this redirect URI to your Google Cloud Console"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate Google OAuth URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OAuth URL: {str(e)}"
        )

@router.post("/google/callback", response_model=Token)
async def google_oauth_callback(
    code: str,
    state: Optional[str] = None,
    redirect_uri: Optional[str] = None
):
    """Handle Google OAuth callback
    
    Creates new user or connects to existing user based on state.
    """
    try:
        # Construct redirect_uri
        if not redirect_uri:
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            redirect_uri = f"{frontend_url}/auth/google/callback"
        
        # Exchange code for tokens and user info
        oauth_data = await OAuthService.exchange_google_code(code, redirect_uri)
        user_info = oauth_data['user_info']
        credentials = oauth_data['credentials']
        
        # Check if connecting to existing user or creating new
        if state and state != 'new_user':
            # Connecting Google to existing account
            user = await db_service.get_document("users", {"id": state})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update user with Google credentials
            await db_service.update_document(
                "users",
                {"id": state},
                {
                    "google_credentials": credentials,
                    "oauth_connected": True,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Create tokens
            access_token = AuthService.create_access_token(
                data={"sub": user["id"], "email": user["email"]}
            )
            refresh_token = AuthService.create_refresh_token(data={"sub": user["id"]})
            
            return Token(access_token=access_token, refresh_token=refresh_token)
        
        else:
            # Check if user exists with this email
            existing_user = await db_service.get_document("users", {"email": user_info['email']})
            
            if existing_user:
                # Link Google to existing account
                await db_service.update_document(
                    "users",
                    {"id": existing_user["id"]},
                    {
                        "google_credentials": credentials,
                        "auth_provider": AuthProvider.GOOGLE,
                        "oauth_connected": True,
                        "email_verified": user_info['email_verified'],
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                )
                user_id = existing_user["id"]
            else:
                # Create new user
                user_id = str(uuid.uuid4())
                user_dict = {
                    "id": user_id,
                    "email": user_info['email'],
                    "full_name": user_info['full_name'],
                    "profile_picture": user_info.get('picture'),
                    "role": "hiring_manager",
                    "auth_provider": AuthProvider.GOOGLE,
                    "google_credentials": credentials,
                    "oauth_connected": True,
                    "is_active": True,
                    "email_verified": user_info['email_verified'],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                await db_service.create_document("users", user_dict)
            
            # Create tokens
            access_token = AuthService.create_access_token(
                data={"sub": user_id, "email": user_info['email']}
            )
            refresh_token = AuthService.create_refresh_token(data={"sub": user_id})
            
            return Token(access_token=access_token, refresh_token=refresh_token)
        
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authentication failed: {str(e)}"
        )

@router.get("/microsoft/url")
async def get_microsoft_oauth_url(
    redirect_uri: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get Microsoft OAuth authorization URL"""
    try:
        # Check if Microsoft credentials are configured
        if not os.environ.get('MICROSOFT_CLIENT_ID'):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Microsoft OAuth not configured. Please set MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET"
            )
        
        # Use provided redirect_uri or construct from frontend URL
        if not redirect_uri:
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            redirect_uri = f"{frontend_url}/auth/microsoft/callback"
        
        # State contains user_id if connecting to existing account
        state = current_user['id'] if current_user else 'new_user'
        
        auth_url = OAuthService.get_microsoft_oauth_url(redirect_uri, state)
        
        return {
            "auth_url": auth_url,
            "redirect_uri": redirect_uri,
            "info": "Add this redirect URI to your Azure App Registration"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate Microsoft OAuth URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OAuth URL: {str(e)}"
        )

@router.post("/microsoft/callback", response_model=Token)
async def microsoft_oauth_callback(
    code: str,
    state: Optional[str] = None,
    redirect_uri: Optional[str] = None
):
    """Handle Microsoft OAuth callback"""
    try:
        # Construct redirect_uri
        if not redirect_uri:
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            redirect_uri = f"{frontend_url}/auth/microsoft/callback"
        
        # Exchange code for tokens and user info
        oauth_data = await OAuthService.exchange_microsoft_code(code, redirect_uri)
        user_info = oauth_data['user_info']
        credentials = oauth_data['credentials']
        
        # Check if connecting to existing user or creating new
        if state and state != 'new_user':
            # Connecting Microsoft to existing account
            user = await db_service.get_document("users", {"id": state})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update user with Microsoft credentials
            await db_service.update_document(
                "users",
                {"id": state},
                {
                    "microsoft_credentials": credentials,
                    "oauth_connected": True,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Create tokens
            access_token = AuthService.create_access_token(
                data={"sub": user["id"], "email": user["email"]}
            )
            refresh_token = AuthService.create_refresh_token(data={"sub": user["id"]})
            
            return Token(access_token=access_token, refresh_token=refresh_token)
        
        else:
            # Check if user exists with this email
            existing_user = await db_service.get_document("users", {"email": user_info['email']})
            
            if existing_user:
                # Link Microsoft to existing account
                await db_service.update_document(
                    "users",
                    {"id": existing_user["id"]},
                    {
                        "microsoft_credentials": credentials,
                        "auth_provider": AuthProvider.MICROSOFT,
                        "oauth_connected": True,
                        "email_verified": user_info['email_verified'],
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                )
                user_id = existing_user["id"]
            else:
                # Create new user
                user_id = str(uuid.uuid4())
                user_dict = {
                    "id": user_id,
                    "email": user_info['email'],
                    "full_name": user_info['full_name'],
                    "role": "hiring_manager",
                    "auth_provider": AuthProvider.MICROSOFT,
                    "microsoft_credentials": credentials,
                    "oauth_connected": True,
                    "is_active": True,
                    "email_verified": user_info['email_verified'],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                await db_service.create_document("users", user_dict)
            
            # Create tokens
            access_token = AuthService.create_access_token(
                data={"sub": user_id, "email": user_info['email']}
            )
            refresh_token = AuthService.create_refresh_token(data={"sub": user_id})
            
            return Token(access_token=access_token, refresh_token=refresh_token)
        
    except Exception as e:
        logger.error(f"Microsoft OAuth callback failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authentication failed: {str(e)}"
        )

@router.post("/disconnect/{provider}")
async def disconnect_oauth(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """Disconnect OAuth provider from user account"""
    try:
        if provider not in ['google', 'microsoft']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid provider. Must be 'google' or 'microsoft'"
            )
        
        # Check if user can disconnect (must have password or other OAuth)
        if not current_user.get('hashed_password'):
            # Check if they have another OAuth provider
            other_provider = 'microsoft' if provider == 'google' else 'google'
            if not current_user.get(f'{other_provider}_credentials'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot disconnect. Please set a password first or connect another provider."
                )
        
        # Remove OAuth credentials
        update_data = {
            f"{provider}_credentials": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update oauth_connected status
        has_other_oauth = bool(current_user.get(f'{other_provider}_credentials'))
        if not has_other_oauth:
            update_data['oauth_connected'] = False
        
        await db_service.update_document(
            "users",
            {"id": current_user["id"]},
            update_data
        )
        
        return {"message": f"{provider.capitalize()} disconnected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth disconnect failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect OAuth: {str(e)}"
        )
