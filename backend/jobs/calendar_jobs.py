"""Calendar background jobs"""
from services.database_service import DatabaseService
from services.calendar_service import CalendarService
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Database setup
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)

def schedule_interview(interview_id: str):
    """Create calendar event for interview"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_schedule_interview_async(interview_id))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Calendar job failed: {str(e)}")
        return {"success": False, "error": str(e)}

async def _schedule_interview_async(interview_id: str):
    """Async implementation of interview scheduling"""
    try:
        # Get interview
        interview = await db_service.get_document("interviews", {"id": interview_id})
        if not interview:
            raise Exception("Interview not found")
        
        # Get application and job
        application = await db_service.get_document("applications", {"id": interview["application_id"]})
        job = await db_service.get_document("jobs", {"id": application["job_id"]})
        company = await db_service.get_document("companies", {"id": job["company_id"]})
        
        # Get user (interviewer) to access calendar credentials
        user = await db_service.get_document("users", {"id": job["created_by"]})
        if not user:
            raise Exception("Interviewer not found")
        
        # Parse datetime
        start_time = datetime.fromisoformat(interview["scheduled_at"].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(interview["end_time"].replace('Z', '+00:00'))
        
        # Create event based on user's calendar provider
        result = None
        
        if user.get('google_credentials'):
            # Use Google Calendar
            result = await CalendarService.create_google_event(
                credentials_dict=user['google_credentials'],
                summary=f"Interview: {job['title']} - {application['candidate_name']}",
                description=f"Interview with {application['candidate_name']} for {job['title']} position.\n\nType: {interview['interview_type']}",
                start_time=start_time,
                end_time=end_time,
                attendees=[application['candidate_email']],
                meeting_link=interview.get('meeting_link')
            )
        
        elif user.get('microsoft_credentials'):
            # Use Outlook Calendar
            result = await CalendarService.create_outlook_event(
                access_token=user['microsoft_credentials']['access_token'],
                summary=f"Interview: {job['title']} - {application['candidate_name']}",
                description=f"Interview with {application['candidate_name']} for {job['title']} position. Type: {interview['interview_type']}",
                start_time=start_time,
                end_time=end_time,
                attendees=[application['candidate_email']],
                meeting_link=interview.get('meeting_link')
            )
        
        if result and result.get('success'):
            # Update interview with calendar event details
            await db_service.update_document(
                "interviews",
                {"id": interview_id},
                {
                    "calendar_event_id": result['event_id'],
                    "calendar_event_link": result.get('event_link'),
                    "meeting_link": result.get('meeting_link') or interview.get('meeting_link')
                }
            )
            logger.info(f"Calendar event created for interview {interview_id}")
            return {"success": True, "event_id": result['event_id']}
        else:
            raise Exception(result.get('error', 'Unknown error') if result else 'No calendar provider configured')
        
    except Exception as e:
        logger.error(f"Interview scheduling failed: {str(e)}")
        raise
