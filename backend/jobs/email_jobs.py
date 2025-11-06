"""Email background jobs"""
from services.database_service import DatabaseService
from services.email_service import EmailService
from services.groq_service import GroqService
from agents.email_agent import EmailAgent
from agents.base_agent import AgentInput
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

# Database setup
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)
groq_service = GroqService()

def send_application_email(application_id: str, email_type: str):
    """Send email to candidate about their application
    
    Args:
        application_id: Application ID
        email_type: Type of email (confirmation, shortlisted, rejected, interview_invite, offer)
    """
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_send_application_email_async(application_id, email_type))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Email job failed: {str(e)}")
        return {"success": False, "error": str(e)}

async def _send_application_email_async(application_id: str, email_type: str):
    """Async implementation of email sending"""
    try:
        # Get application
        application = await db_service.get_document("applications", {"id": application_id})
        if not application:
            raise Exception("Application not found")
        
        # Get job
        job = await db_service.get_document("jobs", {"id": application["job_id"]})
        if not job:
            raise Exception("Job not found")
        
        # Get company
        company = await db_service.get_document("companies", {"id": job["company_id"]})
        if not company:
            raise Exception("Company not found")
        
        # Get email configuration
        email_config = await db_service.get_document("email_configs", {"company_id": company["id"]})
        if not email_config or not email_config.get('is_verified'):
            logger.warning(f"No verified email config for company {company['id']}")
            return {"success": False, "error": "Email not configured"}
        
        # Generate email content using AI
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
                "signature": email_config.get("signature", ""),
                "application": application,
                "job": job
            }
        )
        
        email_result = await email_agent.execute(email_input)
        
        if not email_result.success:
            raise Exception("Failed to generate email content")
        
        email_content = email_result.result
        
        # Send email based on provider
        send_result = None
        
        if email_config['provider'] == 'smtp' and email_config.get('smtp_config'):
            send_result = await EmailService.send_email_smtp(
                smtp_config=email_config['smtp_config'],
                to_email=application['candidate_email'],
                subject=email_content['subject'],
                html_content=email_content['body'],
                from_email=email_config['from_email']
            )
        
        elif email_config['provider'] == 'gmail' and email_config.get('credentials'):
            send_result = await EmailService.send_email_gmail(
                credentials_dict=email_config['credentials'],
                to_email=application['candidate_email'],
                subject=email_content['subject'],
                html_content=email_content['body'],
                from_email=email_config['from_email']
            )
        
        elif email_config['provider'] == 'outlook' and email_config.get('credentials'):
            send_result = await EmailService.send_email_outlook(
                access_token=email_config['credentials']['access_token'],
                to_email=application['candidate_email'],
                subject=email_content['subject'],
                html_content=email_content['body'],
                from_email=email_config['from_email']
            )
        
        if send_result and send_result.get('success'):
            # Log email sent
            await db_service.update_document(
                "applications",
                {"id": application_id},
                {
                    f"emails_sent.{email_type}": {
                        "sent_at": asyncio.get_event_loop().time(),
                        "subject": email_content['subject']
                    }
                }
            )
            logger.info(f"Email sent: {email_type} to {application['candidate_email']}")
            return {"success": True, "email_type": email_type}
        else:
            raise Exception(send_result.get('error', 'Unknown error'))
        
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        raise

def send_interview_reminder(interview_id: str):
    """Send interview reminder email"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_send_interview_reminder_async(interview_id))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Interview reminder job failed: {str(e)}")
        return {"success": False, "error": str(e)}

async def _send_interview_reminder_async(interview_id: str):
    """Async implementation of interview reminder"""
    try:
        # Get interview
        interview = await db_service.get_document("interviews", {"id": interview_id})
        if not interview:
            raise Exception("Interview not found")
        
        # Get application
        application = await db_service.get_document("applications", {"id": interview["application_id"]})
        if not application:
            raise Exception("Application not found")
        
        # Get job and company
        job = await db_service.get_document("jobs", {"id": application["job_id"]})
        company = await db_service.get_document("companies", {"id": job["company_id"]})
        
        # Get email config
        email_config = await db_service.get_document("email_configs", {"company_id": company["id"]})
        if not email_config or not email_config.get('is_verified'):
            return {"success": False, "error": "Email not configured"}
        
        # Generate reminder email
        email_agent = EmailAgent(groq_service)
        email_input = AgentInput(
            task="compose_email",
            context={
                "email_type": "interview_reminder",
                "candidate_name": application["candidate_name"],
                "company_name": company.get("name"),
                "job_title": job["title"],
                "interview": interview,
                "signature": email_config.get("signature", "")
            }
        )
        
        email_result = await email_agent.execute(email_input)
        
        if not email_result.success:
            raise Exception("Failed to generate reminder email")
        
        email_content = email_result.result
        
        # Send email
        send_result = None
        
        if email_config['provider'] == 'gmail' and email_config.get('credentials'):
            send_result = await EmailService.send_email_gmail(
                credentials_dict=email_config['credentials'],
                to_email=application['candidate_email'],
                subject=email_content['subject'],
                html_content=email_content['body'],
                from_email=email_config['from_email']
            )
        elif email_config['provider'] == 'outlook' and email_config.get('credentials'):
            send_result = await EmailService.send_email_outlook(
                access_token=email_config['credentials']['access_token'],
                to_email=application['candidate_email'],
                subject=email_content['subject'],
                html_content=email_content['body'],
                from_email=email_config['from_email']
            )
        elif email_config['provider'] == 'smtp':
            send_result = await EmailService.send_email_smtp(
                smtp_config=email_config['smtp_config'],
                to_email=application['candidate_email'],
                subject=email_content['subject'],
                html_content=email_content['body'],
                from_email=email_config['from_email']
            )
        
        if send_result and send_result.get('success'):
            logger.info(f"Interview reminder sent for interview {interview_id}")
            return {"success": True}
        else:
            raise Exception(send_result.get('error', 'Unknown error'))
        
    except Exception as e:
        logger.error(f"Interview reminder failed: {str(e)}")
        raise
