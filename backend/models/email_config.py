"""Email configuration model"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from enum import Enum

class EmailProvider(str, Enum):
    """Email provider types"""
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    SMTP = "smtp"

class SMTPConfig(BaseModel):
    """SMTP configuration"""
    host: str
    port: int = 587
    username: str
    password: str
    use_tls: bool = True

class EmailConfigBase(BaseModel):
    """Base email configuration"""
    provider: EmailProvider
    from_email: str
    from_name: Optional[str] = None
    signature: Optional[str] = None
    
class EmailConfigCreate(EmailConfigBase):
    """Email configuration for creation"""
    smtp_config: Optional[SMTPConfig] = None
    
class EmailConfig(EmailConfigBase):
    """Email configuration in database"""
    id: str
    company_id: str
    is_verified: bool = False
    oauth_connected: bool = False
    credentials: Optional[Dict[str, Any]] = Field(default=None, exclude=True)
    smtp_config: Optional[Dict[str, Any]] = Field(default=None, exclude=True)
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
