"""Email configuration routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from models.email_config import EmailConfig, EmailConfigCreate, EmailProvider, SMTPConfig
from services.database_service import DatabaseService
from services.email_service import EmailService
from routes.auth_routes import get_current_user
import os
import uuid
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Get database
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
db_service = DatabaseService(db)

@router.post("/", response_model=EmailConfig, status_code=status.HTTP_201_CREATED)
async def create_email_config(
    config_data: EmailConfigCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create or update email configuration for company"""
    try:
        # Get user's company
        company = await db_service.get_document("companies", {"user_id": current_user["id"]})
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please create a company profile first"
            )
        
        # Check if config already exists
        existing_config = await db_service.get_document(
            "email_configs",
            {"company_id": company["id"]}
        )
        
        # Prepare config data
        config_dict = {
            "company_id": company["id"],
            "provider": config_data.provider,
            "from_email": config_data.from_email,
            "from_name": config_data.from_name,
            "signature": config_data.signature,
            "is_verified": False,
            "oauth_connected": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Handle provider-specific configuration
        if config_data.provider == EmailProvider.SMTP and config_data.smtp_config:
            # Store SMTP credentials (in production, encrypt these)
            config_dict["smtp_config"] = config_data.smtp_config.model_dump()
        
        elif config_data.provider in [EmailProvider.GMAIL, EmailProvider.OUTLOOK]:
            # For OAuth providers, check if user has connected their account
            if config_data.provider == EmailProvider.GMAIL:
                if not current_user.get('google_credentials'):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Please connect your Google account first via OAuth"
                    )
                config_dict["credentials"] = current_user['google_credentials']
                config_dict["oauth_connected"] = True
                
            elif config_data.provider == EmailProvider.OUTLOOK:
                if not current_user.get('microsoft_credentials'):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Please connect your Microsoft account first via OAuth"
                    )
                config_dict["credentials"] = current_user['microsoft_credentials']
                config_dict["oauth_connected"] = True
        
        if existing_config:
            # Update existing config
            await db_service.update_document(
                "email_configs",
                {"id": existing_config["id"]},
                config_dict
            )
            config_dict["id"] = existing_config["id"]
            config_dict["created_at"] = existing_config["created_at"]
        else:
            # Create new config
            config_dict["id"] = str(uuid.uuid4())
            config_dict["created_at"] = datetime.now(timezone.utc).isoformat()
            await db_service.create_document("email_configs", config_dict)
        
        # Remove sensitive data from response
        response_config = {k: v for k, v in config_dict.items() if k not in ['credentials', 'smtp_config']}
        
        return response_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create email config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create email configuration: {str(e)}"
        )

@router.get("/", response_model=Optional[EmailConfig])
async def get_email_config(current_user: dict = Depends(get_current_user)):
    """Get email configuration for user's company"""
    try:
        # Get user's company
        company = await db_service.get_document("companies", {"user_id": current_user["id"]})
        if not company:
            return None
        
        # Get email config
        config = await db_service.get_document(
            "email_configs",
            {"company_id": company["id"]}
        )
        
        if not config:
            return None
        
        # Remove sensitive data
        config.pop('credentials', None)
        config.pop('smtp_config', None)
        
        return config
        
    except Exception as e:
        logger.error(f"Failed to get email config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email configuration: {str(e)}"
        )

@router.post("/test")
async def test_email_config(current_user: dict = Depends(get_current_user)):
    """Test email configuration by sending a test email"""
    try:
        # Get user's company
        company = await db_service.get_document("companies", {"user_id": current_user["id"]})
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please create a company profile first"
            )
        
        # Get email config
        config = await db_service.get_document(
            "email_configs",
            {"company_id": company["id"]}
        )
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email configuration not found. Please configure email settings first."
            )
        
        # Test email content
        test_subject = f"Test Email from {company.get('name', 'HireFlow AI')}"
        test_body = f"""
        <html>
            <body>
                <h2>Email Configuration Test</h2>
                <p>This is a test email from HireFlow AI.</p>
                <p>Your email configuration is working correctly!</p>
                <br>
                <p>Company: {company.get('name', 'N/A')}</p>
                <p>Provider: {config['provider']}</p>
                <br>
                {config.get('signature', '')}
            </body>
        </html>
        """
        
        # Send test email based on provider
        result = None
        
        if config['provider'] == 'smtp' and config.get('smtp_config'):
            result = await EmailService.send_email_smtp(
                smtp_config=config['smtp_config'],
                to_email=current_user['email'],
                subject=test_subject,
                html_content=test_body,
                from_email=config['from_email']
            )
        
        elif config['provider'] == 'gmail' and config.get('credentials'):
            result = await EmailService.send_email_gmail(
                credentials_dict=config['credentials'],
                to_email=current_user['email'],
                subject=test_subject,
                html_content=test_body,
                from_email=config['from_email']
            )
        
        elif config['provider'] == 'outlook' and config.get('credentials'):
            result = await EmailService.send_email_outlook(
                access_token=config['credentials']['access_token'],
                to_email=current_user['email'],
                subject=test_subject,
                html_content=test_body,
                from_email=config['from_email']
            )
        
        if result and result.get('success'):
            # Mark config as verified
            await db_service.update_document(
                "email_configs",
                {"id": config["id"]},
                {
                    "is_verified": True,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            return {
                "success": True,
                "message": f"Test email sent successfully to {current_user['email']}",
                "provider": config['provider']
            }
        else:
            return {
                "success": False,
                "message": "Failed to send test email",
                "error": result.get('error') if result else "Unknown error"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test email config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test email configuration: {str(e)}"
        )

@router.delete("/")
async def delete_email_config(current_user: dict = Depends(get_current_user)):
    """Delete email configuration"""
    try:
        # Get user's company
        company = await db_service.get_document("companies", {"user_id": current_user["id"]})
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company not found"
            )
        
        # Delete email config
        result = await db_service.delete_document(
            "email_configs",
            {"company_id": company["id"]}
        )
        
        if result:
            return {"message": "Email configuration deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email configuration not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete email config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete email configuration: {str(e)}"
        )
