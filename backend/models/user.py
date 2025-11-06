from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

class AuthProvider(str, Enum):
    JWT = "jwt"
    GOOGLE = "google"
    MICROSOFT = "microsoft"

class UserRole(str, Enum):
    ADMIN = "admin"
    HIRING_MANAGER = "hiring_manager"
    RECRUITER = "recruiter"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.ADMIN

class UserCreate(UserBase):
    password: Optional[str] = None
    auth_provider: AuthProvider = AuthProvider.JWT

class UserInDB(UserBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    hashed_password: Optional[str] = None
    auth_provider: AuthProvider
    google_id: Optional[str] = None
    microsoft_id: Optional[str] = None
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    auth_provider: AuthProvider
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
