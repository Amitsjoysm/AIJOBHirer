from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum

class InterviewType(str, Enum):
    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"

class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class InterviewFeedback(BaseModel):
    rating: int  # 1-5
    strengths: List[str] = []
    weaknesses: List[str] = []
    notes: str
    recommendation: str  # "strong_hire", "hire", "maybe", "no_hire"

class InterviewBase(BaseModel):
    interview_type: InterviewType
    duration_minutes: int = 60
    notes: Optional[str] = None

class InterviewCreate(InterviewBase):
    application_id: str
    interviewer_id: str
    scheduled_at: datetime
    meeting_link: Optional[str] = None

class InterviewInDB(InterviewBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    application_id: str
    interviewer_id: str
    scheduled_at: datetime
    meeting_link: Optional[str] = None
    status: InterviewStatus = InterviewStatus.SCHEDULED
    feedback: Optional[InterviewFeedback] = None
    google_calendar_event_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Interview(InterviewBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    application_id: str
    scheduled_at: datetime
    status: InterviewStatus
    created_at: datetime
