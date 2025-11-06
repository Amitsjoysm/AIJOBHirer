"""Calendar service for Google Calendar and Outlook Calendar integration"""
from typing import Dict, Any, Optional, List
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CalendarService:
    """Service for managing calendar events across providers"""
    
    @staticmethod
    async def create_google_event(
        credentials_dict: Dict[str, Any],
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[str],
        meeting_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create event in Google Calendar"""
        try:
            creds = Credentials.from_authorized_user_info(credentials_dict)
            service = build('calendar', 'v3', credentials=creds)
            
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': [{'email': email} for email in attendees],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"hireflow-{datetime.now().timestamp()}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                } if not meeting_link else None
            }
            
            if meeting_link:
                event['description'] = f"{description}\n\nMeeting Link: {meeting_link}"
            
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1 if not meeting_link else 0,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Google Calendar event created: {created_event['id']}")
            return {
                "success": True,
                "event_id": created_event['id'],
                "event_link": created_event.get('htmlLink'),
                "meeting_link": created_event.get('hangoutLink', meeting_link)
            }
            
        except Exception as e:
            logger.error(f"Google Calendar event creation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_google_availability(
        credentials_dict: Dict[str, Any],
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get available time slots from Google Calendar"""
        try:
            creds = Credentials.from_authorized_user_info(credentials_dict)
            service = build('calendar', 'v3', credentials=creds)
            
            # Get busy times
            body = {
                'timeMin': start_time.isoformat() + 'Z',
                'timeMax': end_time.isoformat() + 'Z',
                'items': [{'id': 'primary'}]
            }
            
            events_result = service.freebusy().query(body=body).execute()
            busy_times = events_result['calendars']['primary']['busy']
            
            # Calculate available slots (30-minute intervals)
            available_slots = []
            current = start_time
            
            while current < end_time:
                slot_end = current + timedelta(minutes=30)
                
                # Check if slot is free
                is_free = True
                for busy in busy_times:
                    busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                    busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                    
                    if (current >= busy_start and current < busy_end) or \
                       (slot_end > busy_start and slot_end <= busy_end):
                        is_free = False
                        break
                
                if is_free:
                    available_slots.append({
                        'start': current.isoformat(),
                        'end': slot_end.isoformat()
                    })
                
                current = slot_end
            
            return {"success": True, "available_slots": available_slots}
            
        except Exception as e:
            logger.error(f"Google Calendar availability check failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def create_outlook_event(
        access_token: str,
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[str],
        meeting_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create event in Outlook Calendar"""
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            event = {
                'subject': summary,
                'body': {
                    'contentType': 'HTML',
                    'content': description + (f'<br><br>Meeting Link: {meeting_link}' if meeting_link else '')
                },
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'attendees': [
                    {'emailAddress': {'address': email}, 'type': 'required'}
                    for email in attendees
                ],
                'isOnlineMeeting': True if not meeting_link else False,
                'onlineMeetingProvider': 'teamsForBusiness' if not meeting_link else None
            }
            
            response = requests.post(
                'https://graph.microsoft.com/v1.0/me/events',
                headers=headers,
                json=event
            )
            
            if response.status_code == 201:
                event_data = response.json()
                logger.info(f"Outlook event created: {event_data['id']}")
                return {
                    "success": True,
                    "event_id": event_data['id'],
                    "event_link": event_data.get('webLink'),
                    "meeting_link": event_data.get('onlineMeeting', {}).get('joinUrl', meeting_link)
                }
            else:
                logger.error(f"Outlook event creation failed: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Outlook event creation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_outlook_availability(
        access_token: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get available time slots from Outlook Calendar"""
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            body = {
                'schedules': ['me@outlook.com'],
                'startTime': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'endTime': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'availabilityViewInterval': 30
            }
            
            response = requests.post(
                'https://graph.microsoft.com/v1.0/me/calendar/getSchedule',
                headers=headers,
                json=body
            )
            
            if response.status_code == 200:
                schedule_data = response.json()
                # Parse availability view to get free slots
                # This is a simplified version
                return {"success": True, "schedule_data": schedule_data}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Outlook availability check failed: {str(e)}")
            return {"success": False, "error": str(e)}
