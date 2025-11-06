from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from services.database_service import DatabaseService
from services.groq_service import GroqService
from agents.report_agent import ReportAgent
from agents.base_agent import AgentInput
from routes.auth_routes import get_current_user
import os
from typing import Dict, Any
from datetime import datetime, timezone, timedelta

router = APIRouter()

# Get database
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)
groq_service = GroqService()

@router.get("/dashboard")
async def get_dashboard_analytics(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Get dashboard analytics for user's company"""
    
    # Get user's company
    company = await db_service.get_document("companies", {"user_id": current_user["id"]})
    if not company:
        return {
            "total_jobs": 0,
            "active_jobs": 0,
            "total_applications": 0,
            "shortlisted_candidates": 0,
            "interviews_scheduled": 0
        }
    
    # Get jobs
    jobs = await db_service.get_documents("jobs", {"company_id": company["id"]})
    job_ids = [job["id"] for job in jobs]
    
    # Count metrics
    total_jobs = len(jobs)
    active_jobs = len([j for j in jobs if j["status"] == "active"])
    
    # Get applications
    applications = await db_service.get_documents(
        "applications",
        {"job_id": {"$in": job_ids}}
    )
    
    total_applications = len(applications)
    shortlisted = len([a for a in applications if a["status"] == "shortlisted"])
    
    # Get interviews
    application_ids = [app["id"] for app in applications]
    interviews = await db_service.get_documents(
        "interviews",
        {"application_id": {"$in": application_ids}, "status": "scheduled"}
    )
    
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "shortlisted_candidates": shortlisted,
        "interviews_scheduled": len(interviews),
        "recent_applications": applications[:10] if applications else []
    }

@router.get("/jobs/{job_id}/analytics")
async def get_job_analytics(
    job_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get analytics for a specific job"""
    
    # Verify access
    job = await db_service.get_document(
        "jobs",
        {"id": job_id, "created_by": current_user["id"]}
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get applications
    applications = await db_service.get_documents(
        "applications",
        {"job_id": job_id}
    )
    
    # Calculate metrics
    status_counts = {}
    for app in applications:
        status = app["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Calculate average score
    scored_applications = [a for a in applications if a.get("ai_evaluation", {}).get("overall_score")]
    avg_score = 0
    if scored_applications:
        avg_score = sum(a["ai_evaluation"]["overall_score"] for a in scored_applications) / len(scored_applications)
    
    return {
        "job_id": job_id,
        "job_title": job["title"],
        "total_applications": len(applications),
        "view_count": job.get("view_count", 0),
        "status_breakdown": status_counts,
        "average_candidate_score": round(avg_score, 2),
        "top_candidates": sorted(
            [a for a in applications if a.get("ai_evaluation")],
            key=lambda x: x["ai_evaluation"].get("overall_score", 0),
            reverse=True
        )[:5]
    }

@router.post("/report")
async def generate_report(
    report_type: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate AI-powered report"""
    
    # Get user's company
    company = await db_service.get_document("companies", {"user_id": current_user["id"]})
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a company profile first"
        )
    
    # Gather data
    jobs = await db_service.get_documents("jobs", {"company_id": company["id"]})
    job_ids = [job["id"] for job in jobs]
    
    applications = await db_service.get_documents(
        "applications",
        {"job_id": {"$in": job_ids}}
    )
    
    # Use report agent to generate insights
    report_agent = ReportAgent(groq_service)
    agent_input = AgentInput(
        task="generate_report",
        context={
            "report_type": report_type,
            "data": {
                "jobs": jobs,
                "applications": applications,
                "company": company
            },
            "additional_context": {
                "time_period": "last_30_days"
            }
        }
    )
    
    result = await report_agent.execute(agent_input)
    
    if result.success:
        return result.result
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {result.error}"
        )
