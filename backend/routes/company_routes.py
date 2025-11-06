from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorClient
from models.company import CompanyCreate, Company, CompanyBranding, EmailConfig
from services.database_service import DatabaseService
from services.groq_service import GroqService
from agents.persona_creator_agent import PersonaCreatorAgent
from agents.base_agent import AgentInput
from routes.auth_routes import get_current_user
import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

# Get database
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)
groq_service = GroqService()

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    branding: Optional[CompanyBranding] = None
    email_config: Optional[EmailConfig] = None
    auto_reject_after_hours: Optional[int] = None

@router.post("/", response_model=Company, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create a new company profile"""
    
    # Check if slug is available
    existing = await db_service.get_document("companies", {"slug": company_data.slug})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company slug already taken"
        )
    
    # Create company
    company_dict = {
        "id": str(uuid.uuid4()),
        "name": company_data.name,
        "slug": company_data.slug,
        "industry": company_data.industry,
        "website": str(company_data.website) if company_data.website else None,
        "description": company_data.description,
        "user_id": current_user["id"],
        "auto_reject_after_hours": 48,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db_service.create_document("companies", company_dict)
    
    # Generate persona in background
    if company_data.website:
        background_tasks.add_task(generate_company_persona, company_dict["id"], company_data)
    
    return company_dict

async def generate_company_persona(company_id: str, company_data: CompanyCreate):
    """Background task to generate company persona"""
    try:
        persona_agent = PersonaCreatorAgent(groq_service)
        agent_input = AgentInput(
            task="create_persona",
            context={
                "company_name": company_data.name,
                "industry": company_data.industry,
                "description": company_data.description,
                "website_url": str(company_data.website) if company_data.website else None
            }
        )
        
        result = await persona_agent.execute(agent_input)
        
        if result.success:
            await db_service.update_document(
                "companies",
                {"id": company_id},
                {"persona": result.result}
            )
    except Exception as e:
        print(f"Failed to generate persona: {str(e)}")

@router.get("/", response_model=list[Company])
async def get_my_companies(current_user: dict = Depends(get_current_user)):
    """Get all companies for current user"""
    companies = await db_service.get_documents("companies", {"user_id": current_user["id"]})
    return companies

@router.get("/{company_id}", response_model=Company)
async def get_company(company_id: str, current_user: dict = Depends(get_current_user)):
    """Get company by ID"""
    company = await db_service.get_document("companies", {"id": company_id, "user_id": current_user["id"]})
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company

@router.get("/slug/{slug}", response_model=Company)
async def get_company_by_slug(slug: str):
    """Get company by slug (public endpoint for career page)"""
    company = await db_service.get_document("companies", {"slug": slug})
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company

@router.patch("/{company_id}", response_model=Company)
async def update_company(
    company_id: str,
    update_data: CompanyUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update company profile"""
    
    # Verify ownership
    company = await db_service.get_document("companies", {"id": company_id, "user_id": current_user["id"]})
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update
    update_dict = update_data.model_dump(exclude_unset=True)
    if update_dict:
        await db_service.update_document("companies", {"id": company_id}, update_dict)
    
    # Get updated company
    updated_company = await db_service.get_document("companies", {"id": company_id})
    return updated_company
