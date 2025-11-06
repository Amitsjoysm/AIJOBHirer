from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorClient
from models.job import JobCreate, Job, JobStatus, JobInDB
from services.database_service import DatabaseService
from services.groq_service import GroqService
from agents.job_creation_agent import JobCreationAgent
from agents.base_agent import AgentInput
from routes.auth_routes import get_current_user
import os
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter()

# Get database
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)
groq_service = GroqService()

class JobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None

@router.post("/", response_model=Job, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create a new job posting"""
    
    # Get user's company
    company = await db_service.get_document("companies", {"user_id": current_user["id"]})
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a company profile first"
        )
    
    # Create job
    job_dict = {
        "id": str(uuid.uuid4()),
        "company_id": company["id"],
        "created_by": current_user["id"],
        "title": job_data.title,
        "department": job_data.department,
        "description": job_data.description,
        "requirements": job_data.requirements,
        "nice_to_have": job_data.nice_to_have,
        "job_type": job_data.job_type,
        "location_type": job_data.location_type,
        "location": job_data.location,
        "experience_level": job_data.experience_level,
        "salary_min": job_data.salary_min,
        "salary_max": job_data.salary_max,
        "salary_currency": job_data.salary_currency,
        "screening_questions": [q.model_dump() for q in job_data.screening_questions],
        "status": JobStatus.DRAFT,
        "ai_generated": job_data.use_ai_generation,
        "view_count": 0,
        "application_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "published_at": None
    }
    
    # If AI generation requested, generate content
    if job_data.use_ai_generation:
        background_tasks.add_task(generate_job_content, job_dict["id"], job_data, company)
    
    await db_service.create_document("jobs", job_dict)
    
    return job_dict

async def generate_job_content(job_id: str, job_data: JobCreate, company: dict):
    """Background task to generate job content with AI"""
    try:
        job_agent = JobCreationAgent(groq_service)
        
        context = {
            "title": job_data.title,
            "department": job_data.department,
            "experience_level": job_data.experience_level,
            "job_type": job_data.job_type,
            "location_type": job_data.location_type,
            "ai_input": job_data.ai_input,
            "company_values": company.get("persona", {}).get("company_values", []),
            "requirements": job_data.requirements
        }
        
        agent_input = AgentInput(task="generate_job_content", context=context)
        result = await job_agent.execute(agent_input)
        
        if result.success:
            update_data = {
                "description": result.result["description"],
                "requirements": result.result["requirements"],
                "nice_to_have": result.result["nice_to_have"],
                "screening_questions": result.result["screening_questions"]
            }
            await db_service.update_document("jobs", {"id": job_id}, update_data)
    except Exception as e:
        print(f"Failed to generate job content: {str(e)}")

@router.get("/company/{company_id}", response_model=List[Job])
async def get_company_jobs(company_id: str, status: Optional[JobStatus] = None):
    """Get all jobs for a company (public for career page)"""
    query = {"company_id": company_id}
    if status:
        query["status"] = status
    else:
        query["status"] = JobStatus.ACTIVE
    
    jobs = await db_service.get_documents("jobs", query, sort=[("created_at", -1)])
    return jobs

@router.get("/my-jobs", response_model=List[Job])
async def get_my_jobs(current_user: dict = Depends(get_current_user)):
    """Get all jobs created by current user"""
    jobs = await db_service.get_documents(
        "jobs",
        {"created_by": current_user["id"]},
        sort=[("created_at", -1)]
    )
    return jobs

@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get job by ID (public)"""
    job = await db_service.get_document("jobs", {"id": job_id})
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Increment view count
    await db_service.update_document(
        "jobs",
        {"id": job_id},
        {"view_count": job.get("view_count", 0) + 1}
    )
    
    return job

@router.patch("/{job_id}", response_model=Job)
async def update_job(
    job_id: str,
    update_data: JobUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update job"""
    
    # Verify ownership
    job = await db_service.get_document("jobs", {"id": job_id, "created_by": current_user["id"]})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Update
    update_dict = update_data.model_dump(exclude_unset=True)
    if update_dict:
        # If publishing, set published_at
        if update_dict.get("status") == JobStatus.ACTIVE and job["status"] != JobStatus.ACTIVE:
            update_dict["published_at"] = datetime.now(timezone.utc).isoformat()
        
        await db_service.update_document("jobs", {"id": job_id}, update_dict)
    
    # Get updated job
    updated_job = await db_service.get_document("jobs", {"id": job_id})
    return updated_job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """Delete job"""
    
    # Verify ownership
    job = await db_service.get_document("jobs", {"id": job_id, "created_by": current_user["id"]})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    await db_service.delete_document("jobs", {"id": job_id})
    return {"message": "Job deleted"}
