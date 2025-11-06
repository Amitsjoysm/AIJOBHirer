from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

class WorkExperience(BaseModel):
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None

class ParsedResume(BaseModel):
    work_experience: List[WorkExperience] = []
    education: List[Education] = []
    skills: List[str] = []
    certifications: List[str] = []
    summary: Optional[str] = None

class CandidateBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateInDB(CandidateBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    parsed_resume: Optional[ParsedResume] = None
    resume_urls: List[str] = []
    application_ids: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Candidate(CandidateBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    parsed_resume: Optional[ParsedResume]
    created_at: datetime
