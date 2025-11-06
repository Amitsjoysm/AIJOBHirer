from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from models.candidate import Candidate
from services.database_service import DatabaseService
from routes.auth_routes import get_current_user
import os
from typing import List

router = APIRouter()

# Get database
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)

@router.get("/", response_model=List[Candidate])
async def get_candidates(current_user: dict = Depends(get_current_user)):
    """Get all candidates for user's company"""
    
    # Get user's company
    company = await db_service.get_document("companies", {"user_id": current_user["id"]})
    if not company:
        return []
    
    # Get all jobs for company
    jobs = await db_service.get_documents("jobs", {"company_id": company["id"]})
    job_ids = [job["id"] for job in jobs]
    
    # Get all applications for these jobs
    applications = await db_service.get_documents(
        "applications",
        {"job_id": {"$in": job_ids}}
    )
    
    # Get unique candidate IDs
    candidate_ids = list(set(app["candidate_id"] for app in applications))
    
    # Get candidates
    candidates = await db_service.get_documents(
        "candidates",
        {"id": {"$in": candidate_ids}}
    )
    
    return candidates

@router.get("/{candidate_id}", response_model=Candidate)
async def get_candidate(
    candidate_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get candidate by ID"""
    
    candidate = await db_service.get_document("candidates", {"id": candidate_id})
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    return candidate
