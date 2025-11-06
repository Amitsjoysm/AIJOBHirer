from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from services.database_service import DatabaseService
from services.groq_service import GroqService
from agents.orchestrator_agent import OrchestratorAgent
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

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    action_taken: Optional[str] = None
    data: Optional[dict] = None

@router.post("/", response_model=ChatResponse)
async def chat_with_orchestrator(
    chat_message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """
    Chat with the AI Orchestrator agent.
    The orchestrator can help with various tasks like creating jobs,
    analyzing candidates, scheduling interviews, etc.
    """
    
    # Create or retrieve session
    session_id = chat_message.session_id or str(uuid.uuid4())
    
    # Get conversation history
    conversation_history = []
    if chat_message.session_id:
        history = await db_service.get_documents(
            "chat_history",
            {"session_id": session_id, "user_id": current_user["id"]},
            sort=[("created_at", 1)],
            limit=10
        )
        conversation_history = [
            {"role": h["role"], "content": h["content"]} 
            for h in history
        ]
    
    # Get user's company context
    company = await db_service.get_document("companies", {"user_id": current_user["id"]})
    
    # Get recent jobs and applications for context
    jobs = []
    applications = []
    if company:
        jobs = await db_service.get_documents(
            "jobs",
            {"company_id": company["id"]},
            sort=[("created_at", -1)],
            limit=5
        )
        job_ids = [job["id"] for job in jobs]
        if job_ids:
            applications = await db_service.get_documents(
                "applications",
                {"job_id": {"$in": job_ids}},
                sort=[("created_at", -1)],
                limit=10
            )
    
    # Prepare orchestrator input
    orchestrator = OrchestratorAgent(groq_service)
    agent_input = AgentInput(
        task="process_chat",
        context={
            "message": chat_message.message,
            "user_id": current_user["id"],
            "company": company,
            "jobs": jobs,
            "applications": applications,
            "conversation_history": conversation_history
        }
    )
    
    # Execute orchestrator
    result = await orchestrator.execute(agent_input)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat: {result.error}"
        )
    
    # Save to chat history
    await db_service.create_document("chat_history", {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "user_id": current_user["id"],
        "role": "user",
        "content": chat_message.message,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    await db_service.create_document("chat_history", {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "user_id": current_user["id"],
        "role": "assistant",
        "content": result.result.get("response", ""),
        "action_taken": result.result.get("action_taken"),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return ChatResponse(
        response=result.result.get("response", "I'm here to help with your hiring needs!"),
        session_id=session_id,
        action_taken=result.result.get("action_taken"),
        data=result.result.get("data")
    )

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get chat history for a session"""
    
    history = await db_service.get_documents(
        "chat_history",
        {"session_id": session_id, "user_id": current_user["id"]},
        sort=[("created_at", 1)]
    )
    
    return history

@router.get("/sessions")
async def get_chat_sessions(current_user: dict = Depends(get_current_user)):
    """Get all chat sessions for the current user"""
    
    # Aggregate to get unique sessions with latest message
    pipeline = [
        {"$match": {"user_id": current_user["id"]}},
        {"$sort": {"created_at": -1}},
        {
            "$group": {
                "_id": "$session_id",
                "last_message": {"$first": "$content"},
                "last_updated": {"$first": "$created_at"},
                "message_count": {"$sum": 1}
            }
        },
        {"$sort": {"last_updated": -1}},
        {"$limit": 20}
    ]
    
    sessions = await db.chat_history.aggregate(pipeline).to_list(20)
    
    return [
        {
            "session_id": s["_id"],
            "last_message": s["last_message"][:100] + "..." if len(s["last_message"]) > 100 else s["last_message"],
            "last_updated": s["last_updated"],
            "message_count": s["message_count"]
        }
        for s in sessions
    ]

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a chat session"""
    
    # Delete all messages in the session
    result = await db.chat_history.delete_many(
        {"session_id": session_id, "user_id": current_user["id"]}
    )
    
    return {"message": f"Session deleted successfully. Removed {result.deleted_count} messages."}
