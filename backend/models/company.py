from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

class EmailConfig(BaseModel):
    provider: str  # 'gmail', 'outlook', 'smtp'
    email: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    use_oauth: bool = False
    oauth_token: Optional[str] = None
    signature: Optional[str] = None

class CompanyPersona(BaseModel):
    company_mission: Optional[str] = None
    company_values: List[str] = []
    company_culture: Optional[str] = None
    hiring_style: Optional[str] = None
    tone: str = "professional"  # professional, casual, friendly

class CompanyBranding(BaseModel):
    logo_url: Optional[str] = None
    primary_color: str = "#3B82F6"
    secondary_color: str = "#10B981"
    header_image_url: Optional[str] = None
    about_us: Optional[str] = None

class CompanyBase(BaseModel):
    name: str
    industry: str
    website: Optional[HttpUrl] = None
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    slug: str

class CompanyInDB(CompanyBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    slug: str
    user_id: str
    email_config: Optional[EmailConfig] = None
    persona: Optional[CompanyPersona] = None
    branding: Optional[CompanyBranding] = None
    google_calendar_token: Optional[str] = None
    outlook_calendar_token: Optional[str] = None
    auto_reject_after_hours: int = 48
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Company(CompanyBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    slug: str
    user_id: str
    email_config: Optional[EmailConfig] = None
    persona: Optional[CompanyPersona] = None
    branding: Optional[CompanyBranding] = None
    auto_reject_after_hours: int
    created_at: datetime
    updated_at: datetime
