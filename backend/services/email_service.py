"""Email service supporting multiple providers (Gmail, Outlook, SMTP)"""
from typing import Dict, Any, Optional, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
import logging
import os

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via multiple providers"""
    
    @staticmethod
    async def send_email_smtp(
        smtp_config: Dict[str, Any],
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email via custom SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or smtp_config.get('username')
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Connect to SMTP server
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent via SMTP to {to_email}")
            return {"success": True, "message": "Email sent successfully"}
            
        except Exception as e:
            logger.error(f"SMTP email failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def send_email_gmail(
        credentials_dict: Dict[str, Any],
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str
    ) -> Dict[str, Any]:
        """Send email via Gmail API"""
        try:
            creds = Credentials.from_authorized_user_info(credentials_dict)
            service = build('gmail', 'v1', credentials=creds)
            
            message = MIMEMultipart('alternative')
            message['to'] = to_email
            message['from'] = from_email
            message['subject'] = subject
            
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_result = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent via Gmail to {to_email}")
            return {"success": True, "message_id": send_result['id']}
            
        except Exception as e:
            logger.error(f"Gmail API email failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def send_email_outlook(
        access_token: str,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str
    ) -> Dict[str, Any]:
        """Send email via Microsoft Graph API"""
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            email_msg = {
                'message': {
                    'subject': subject,
                    'body': {
                        'contentType': 'HTML',
                        'content': html_content
                    },
                    'toRecipients': [
                        {
                            'emailAddress': {
                                'address': to_email
                            }
                        }
                    ]
                },
                'saveToSentItems': 'true'
            }
            
            response = requests.post(
                'https://graph.microsoft.com/v1.0/me/sendMail',
                headers=headers,
                json=email_msg
            )
            
            if response.status_code == 202:
                logger.info(f"Email sent via Outlook to {to_email}")
                return {"success": True, "message": "Email sent successfully"}
            else:
                logger.error(f"Outlook API error: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Outlook API email failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def test_email_connection(
        email_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test email configuration"""
        provider = email_config.get('provider', 'smtp')
        
        try:
            if provider == 'smtp':
                server = smtplib.SMTP(email_config['host'], email_config['port'], timeout=10)
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.quit()
                return {"success": True, "message": "SMTP connection successful"}
            
            elif provider == 'gmail':
                # Test Gmail API access
                creds = Credentials.from_authorized_user_info(email_config['credentials'])
                service = build('gmail', 'v1', credentials=creds)
                profile = service.users().getProfile(userId='me').execute()
                return {"success": True, "message": f"Gmail connected: {profile['emailAddress']}"}
            
            elif provider == 'outlook':
                # Test Microsoft Graph API access
                import requests
                headers = {'Authorization': f'Bearer {email_config["access_token"]}'}
                response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    return {"success": True, "message": f"Outlook connected: {user_data['mail']}"}
                else:
                    return {"success": False, "error": "Invalid Outlook access token"}
            
            return {"success": False, "error": "Unknown provider"}
            
        except Exception as e:
            logger.error(f"Email test failed: {str(e)}")
            return {"success": False, "error": str(e)}
