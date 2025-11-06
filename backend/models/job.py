from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum

class JobStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"

class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"

class LocationType(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    LEAD = "lead"

class ScreeningQuestion(BaseModel):
    question: str
    question_type: str = "text"  # text, multiple_choice, yes_no
    options: Optional[List[str]] = None
    required: bool = True
    weight: float = 1.0

class JobBase(BaseModel):
    title: str
    department: str
    description: str
    requirements: List[str] = []
    nice_to_have: List[str] = []
    job_type: JobType = JobType.FULL_TIME
    location_type: LocationType = LocationType.REMOTE
    location: Optional[str] = None
    experience_level: ExperienceLevel = ExperienceLevel.INTERMEDIATE
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"

class JobCreate(JobBase):
    screening_questions: List[ScreeningQuestion] = []
    use_ai_generation: bool = False
    ai_input: Optional[str] = None

class JobInDB(JobBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    company_id: str
    created_by: str
    status: JobStatus = JobStatus.DRAFT
    screening_questions: List[ScreeningQuestion] = []
    ai_generated: bool = False
    view_count: int = 0
    application_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None

class Job(JobBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    company_id: str
    status: JobStatus
    screening_questions: List[ScreeningQuestion]
    application_count: int
    created_at: datetime
    published_at: Optional[datetime]
