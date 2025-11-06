from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorClient
from models.application import ApplicationCreate, Application, ApplicationStatus
from models.candidate import CandidateCreate
from services.database_service import DatabaseService
from services.groq_service import GroqService
from agents.resume_parser_agent import ResumeParserAgent
from agents.email_agent import EmailAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.base_agent import AgentInput
from routes.auth_routes import get_current_user
import os
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
import PyPDF2
import io
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Get database
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)
groq_service = GroqService()

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    notes: Optional[str] = None

@router.post("/", response_model=Application, status_code=status.HTTP_201_CREATED)
async def submit_application(
    application_data: ApplicationCreate,
    background_tasks: BackgroundTasks
):
    """Submit a job application (public endpoint)"""
    
    # Verify job exists
    job = await db_service.get_document("jobs", {"id": application_data.job_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not accepting applications"
        )
    
    # Create or get candidate
    candidate = await db_service.get_document("candidates", {"email": application_data.candidate_email})
    
    if not candidate:
        candidate = {
            "id": str(uuid.uuid4()),
            "email": application_data.candidate_email,
            "full_name": application_data.candidate_name,
            "phone": application_data.candidate_phone,
            "linkedin_url": application_data.candidate_linkedin,
            "resume_urls": [application_data.resume_url],
            "application_ids": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db_service.create_document("candidates", candidate)
    
    # Create application
    application = {
        "id": str(uuid.uuid4()),
        "job_id": application_data.job_id,
        "candidate_id": candidate["id"],
        "candidate_email": application_data.candidate_email,
        "candidate_name": application_data.candidate_name,
        "candidate_phone": application_data.candidate_phone,
        "candidate_linkedin": application_data.candidate_linkedin,
        "resume_url": application_data.resume_url,
        "questionnaire_answers": [a.model_dump() for a in application_data.questionnaire_answers],
        "status": ApplicationStatus.SUBMITTED,
        "notes": [],
        "tags": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db_service.create_document("applications", application)
    
    # Update job application count
    await db_service.update_document(
        "jobs",
        {"id": application_data.job_id},
        {"application_count": job.get("application_count", 0) + 1}
    )
    
    # Update candidate applications
    candidate_app_ids = candidate.get("application_ids", [])
    candidate_app_ids.append(application["id"])
    await db_service.update_document(
        "candidates",
        {"id": candidate["id"]},
        {"application_ids": candidate_app_ids, "resume_urls": [application_data.resume_url]}
    )
    
    # Process application in background
    background_tasks.add_task(process_application, application["id"], job)
    
    return application

async def process_application(application_id: str, job: dict):
    """Background task to process application with AI and send emails"""
    try:
        # Get application
        application = await db_service.get_document("applications", {"id": application_id})
        if not application:
            return
        
        # Update status to screening
        await db_service.update_document(
            "applications",
            {"id": application_id},
            {"status": ApplicationStatus.SCREENING}
        )
        
        # Parse resume (mock - in production, fetch and parse actual resume)
        resume_text = """Mock resume text for demonstration.
        Experience: Senior Software Engineer at TechCorp (2020-2023)
        Education: BS Computer Science, MIT
        Skills: Python, FastAPI, React, Machine Learning
        """
        
        resume_parser = ResumeParserAgent(groq_service)
        
        # Get company for values
        company = await db_service.get_document("companies", {"id": job["company_id"]})
        company_values = company.get("persona", {}).get("company_values", []) if company else []
        
        parse_input = AgentInput(
            task="parse_and_evaluate",
            context={
                "resume_text": resume_text,
                "job_description": job,
                "questionnaire_answers": application["questionnaire_answers"],
                "company_values": company_values
            }
        )
        
        parse_result = await resume_parser.execute(parse_input)
        
        if parse_result.success:
            # Update candidate with parsed resume
            await db_service.update_document(
                "candidates",
                {"id": application["candidate_id"]},
                {"parsed_resume": parse_result.result["parsed_resume"]}
            )
            
            # Update application with evaluation
            evaluation = parse_result.result["evaluation"]
            await db_service.update_document(
                "applications",
                {"id": application_id},
                {"ai_evaluation": evaluation}
            )
            
            # Queue confirmation email
            try:
                from services.queue_service import QueueService
                from jobs.email_jobs import send_application_email
                
                queue_service = QueueService()
                queue_service.enqueue_email_job(
                    send_application_email,
                    application_id,
                    "confirmation"
                )
                logger.info(f"Confirmation email queued for application {application_id}")
            except Exception as e:
                logger.error(f"Failed to queue confirmation email: {str(e)}")
            
            # If strong match, update status and send shortlisted email
            if evaluation and evaluation.get("recommendation") == "strong_match":
                await db_service.update_document(
                    "applications",
                    {"id": application_id},
                    {"status": ApplicationStatus.SHORTLISTED}
                )
                
                # Queue shortlisted email
                try:
                    queue_service.enqueue_email_job(
                        send_application_email,
                        application_id,
                        "shortlisted"
                    )
                    logger.info(f"Shortlisted email queued for application {application_id}")
                except Exception as e:
                    logger.error(f"Failed to queue shortlisted email: {str(e)}")
            
            # If not a good match, schedule rejection email (after delay)
            elif evaluation and evaluation.get("recommendation") == "not_a_fit":
                # Queue rejection email to be sent after 48 hours (configurable)
                try:
                    from rq.job import Job
                    from datetime import timedelta
                    
                    queue_service.email_queue.enqueue_in(
                        timedelta(hours=48),
                        send_application_email,
                        application_id,
                        "rejected"
                    )
                    logger.info(f"Rejection email scheduled for application {application_id} (48h delay)")
                except Exception as e:
                    logger.error(f"Failed to schedule rejection email: {str(e)}")
        
    except Exception as e:
        logger.error(f\"Failed to process application: {str(e)}\")

@router.get("/job/{job_id}", response_model=List[Application])
async def get_job_applications(
    job_id: str,
    status: Optional[ApplicationStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all applications for a job"""
    
    # Verify user owns the job
    job = await db_service.get_document("jobs", {"id": job_id, "created_by": current_user["id"]})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    query = {"job_id": job_id}
    if status:
        query["status"] = status
    
    applications = await db_service.get_documents(
        "applications",
        query,
        sort=[("created_at", -1)]
    )
    
    return applications

@router.get("/{application_id}", response_model=Application)
async def get_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get application by ID"""
    
    application = await db_service.get_document("applications", {"id": application_id})
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify user owns the job
    job = await db_service.get_document(
        "jobs",
        {"id": application["job_id"], "created_by": current_user["id"]}
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return application

@router.patch("/{application_id}/status", response_model=Application)
async def update_application_status(
    application_id: str,
    status_update: ApplicationStatusUpdate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Update application status"""
    
    application = await db_service.get_document("applications", {"id": application_id})
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify ownership
    job = await db_service.get_document(
        "jobs",
        {"id": application["job_id"], "created_by": current_user["id"]}
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update status
    update_data = {"status": status_update.status}
    
    if status_update.notes:
        notes = application.get("notes", [])
        notes.append({
            "text": status_update.notes,
            "created_by": current_user["id"],
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        update_data["notes"] = notes
    
    await db_service.update_document("applications", {"id": application_id}, update_data)
    
    # Send appropriate email based on status
    background_tasks.add_task(send_status_email, application_id, status_update.status)
    
    # Get updated application
    updated_application = await db_service.get_document("applications", {"id": application_id})
    return updated_application

async def send_status_email(application_id: str, new_status: ApplicationStatus):
    """Send email based on application status change"""
    try:
        application = await db_service.get_document("applications", {"id": application_id})
        job = await db_service.get_document("jobs", {"id": application["job_id"]})
        company = await db_service.get_document("companies", {"id": job["company_id"]})
        
        email_type_map = {
            ApplicationStatus.REJECTED: "rejected",
            ApplicationStatus.OFFER: "offer"
        }
        
        email_type = email_type_map.get(new_status)
        if not email_type:
            return
        
        email_agent = EmailAgent(groq_service)
        email_input = AgentInput(
            task="compose_email",
            context={
                "email_type": email_type,
                "candidate_name": application["candidate_name"],
                "company_name": company.get("name", "Our Company"),
                "job_title": job["title"],
                "tone": company.get("persona", {}).get("tone", "professional"),
                "persona": company.get("persona", {}),
                "signature": company.get("email_config", {}).get("signature", "")
            }
        )
        
        await email_agent.execute(email_input)
        
    except Exception as e:
        print(f"Failed to send status email: {str(e)}")
