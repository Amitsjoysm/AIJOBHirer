from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorClient
from models.interview import InterviewCreate, Interview, InterviewStatus, InterviewFeedback
from services.database_service import DatabaseService
from services.groq_service import GroqService
from agents.calendar_agent import CalendarAgent
from agents.email_agent import EmailAgent
from agents.base_agent import AgentInput
from routes.auth_routes import get_current_user
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

# Get database
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)
groq_service = GroqService()

class InterviewUpdate(BaseModel):
    status: Optional[InterviewStatus] = None
    feedback: Optional[InterviewFeedback] = None

@router.post("", response_model=Interview, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=Interview, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    interview_data: InterviewCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Schedule an interview"""
    
    # Verify application exists and user has access
    application = await db_service.get_document("applications", {"id": interview_data.application_id})
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    job = await db_service.get_document(
        "jobs",
        {"id": application["job_id"], "created_by": current_user["id"]}
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Create interview
    interview = {
        "id": str(uuid.uuid4()),
        "application_id": interview_data.application_id,
        "interviewer_id": interview_data.interviewer_id,
        "interview_type": interview_data.interview_type,
        "scheduled_at": interview_data.scheduled_at.isoformat(),
        "duration_minutes": interview_data.duration_minutes,
        "meeting_link": interview_data.meeting_link,
        "notes": interview_data.notes,
        "status": InterviewStatus.SCHEDULED,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db_service.create_document("interviews", interview)
    
    # Update application status
    await db_service.update_document(
        "applications",
        {"id": interview_data.application_id},
        {"status": "interview_scheduled"}
    )
    
    # Send interview invitation email
    background_tasks.add_task(send_interview_invitation, interview["id"])
    
    return interview

async def send_interview_invitation(interview_id: str):
    """Send interview invitation email to candidate"""
    try:
        interview = await db_service.get_document("interviews", {"id": interview_id})
        application = await db_service.get_document("applications", {"id": interview["application_id"]})
        job = await db_service.get_document("jobs", {"id": application["job_id"]})
        company = await db_service.get_document("companies", {"id": job["company_id"]})
        
        email_agent = EmailAgent(groq_service)
        email_input = AgentInput(
            task="compose_email",
            context={
                "email_type": "interview_invite",
                "candidate_name": application["candidate_name"],
                "company_name": company.get("name", "Our Company"),
                "job_title": job["title"],
                "tone": company.get("persona", {}).get("tone", "professional"),
                "persona": company.get("persona", {}),
                "signature": company.get("email_config", {}).get("signature", ""),
                "additional_context": {
                    "interview_date": interview["scheduled_at"],
                    "interview_type": interview["interview_type"],
                    "duration": interview["duration_minutes"],
                    "meeting_link": interview.get("meeting_link", "")
                }
            }
        )
        
        await email_agent.execute(email_input)
        
    except Exception as e:
        print(f"Failed to send interview invitation: {str(e)}")

@router.get("/application/{application_id}", response_model=List[Interview])
async def get_application_interviews(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all interviews for an application"""
    
    # Verify access
    application = await db_service.get_document("applications", {"id": application_id})
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    job = await db_service.get_document(
        "jobs",
        {"id": application["job_id"], "created_by": current_user["id"]}
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    interviews = await db_service.get_documents(
        "interviews",
        {"application_id": application_id},
        sort=[("scheduled_at", -1)]
    )
    
    return interviews

@router.patch("/{interview_id}", response_model=Interview)
async def update_interview(
    interview_id: str,
    update_data: InterviewUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update interview (add feedback, change status)"""
    
    interview = await db_service.get_document("interviews", {"id": interview_id})
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Verify access
    application = await db_service.get_document("applications", {"id": interview["application_id"]})
    job = await db_service.get_document(
        "jobs",
        {"id": application["job_id"], "created_by": current_user["id"]}
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update
    update_dict = update_data.model_dump(exclude_unset=True)
    if update_dict:
        await db_service.update_document("interviews", {"id": interview_id}, update_dict)
    
    # If interview completed with feedback, update application status
    if update_data.feedback:
        recommendation = update_data.feedback.recommendation
        if recommendation in ["strong_hire", "hire"]:
            await db_service.update_document(
                "applications",
                {"id": interview["application_id"]},
                {"status": "interviewed"}
            )
        elif recommendation == "no_hire":
            await db_service.update_document(
                "applications",
                {"id": interview["application_id"]},
                {"status": "rejected"}
            )
    
    # Get updated interview
    updated_interview = await db_service.get_document("interviews", {"id": interview_id})
    return updated_interview
