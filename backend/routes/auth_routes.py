from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from models.user import UserCreate, User, Token, AuthProvider
from services.auth_service import AuthService
from services.database_service import DatabaseService
import os
import uuid
from datetime import datetime, timezone

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Get database
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Dependency to get current user from token"""
    payload = AuthService.decode_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = await db_service.get_document("users", {"id": user_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user with email/password"""
    
    # Check if user already exists
    existing_user = await db_service.get_document("users", {"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    if not user_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required"
        )
    
    hashed_password = AuthService.get_password_hash(user_data.password)
    
    # Create user
    user_dict = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "hashed_password": hashed_password,
        "auth_provider": AuthProvider.JWT,
        "is_active": True,
        "email_verified": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db_service.create_document("users", user_dict)
    
    # Create tokens
    access_token = AuthService.create_access_token(data={"sub": user_dict["id"], "email": user_dict["email"]})
    refresh_token = AuthService.create_refresh_token(data={"sub": user_dict["id"]})
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email/password"""
    
    # Get user
    user = await db_service.get_document("users", {"email": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not AuthService.verify_password(form_data.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    access_token = AuthService.create_access_token(data={"sub": user["id"], "email": user["email"]})
    refresh_token = AuthService.create_refresh_token(data={"sub": user["id"]})
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.get("/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@router.post("/google")
async def google_auth(code: str):
    """Google OAuth callback"""
    # TODO: Implement Google OAuth flow
    # This would exchange the code for tokens, get user info, and create/login user
    raise HTTPException(status_code=501, detail="Google OAuth not yet implemented")
