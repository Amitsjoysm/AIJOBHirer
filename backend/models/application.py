from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum

class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    SCREENING = "screening"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class ScoreBreakdown(BaseModel):
    skills_match: float = 0.0
    experience_relevance: float = 0.0
    education_fit: float = 0.0
    career_trajectory: float = 0.0
    questionnaire_score: float = 0.0

class AIEvaluation(BaseModel):
    overall_score: float = 0.0
    score_breakdown: ScoreBreakdown
    summary: str
    strengths: List[str] = []
    concerns: List[str] = []
    recommendation: str  # "strong_match", "consider", "not_a_fit"

class QuestionnaireAnswer(BaseModel):
    question: str
    answer: str
    score: Optional[float] = None

class ApplicationBase(BaseModel):
    candidate_email: EmailStr
    candidate_name: str
    candidate_phone: Optional[str] = None
    candidate_linkedin: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    job_id: str
    resume_url: str
    questionnaire_answers: List[QuestionnaireAnswer] = []

class ApplicationInDB(ApplicationBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    job_id: str
    candidate_id: str
    resume_url: str
    questionnaire_answers: List[QuestionnaireAnswer] = []
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    ai_evaluation: Optional[AIEvaluation] = None
    notes: List[Dict[str, Any]] = []
    tags: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: Optional[datetime] = None

class Application(ApplicationBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    job_id: str
    candidate_id: str
    status: ApplicationStatus
    ai_evaluation: Optional[AIEvaluation]
    created_at: datetime
