from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
import json

class CalendarAgent(BaseAgent):
    """Agent for managing calendar and scheduling interviews"""
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Handle calendar-related tasks"""
        self._log(f"Calendar task: {input_data.task}")
        
        try:
            task_type = input_data.context.get('task_type', 'find_slots')
            
            if task_type == 'find_slots':
                result = await self._find_available_slots(input_data.context)
            elif task_type == 'resolve_conflict':
                result = await self._resolve_conflict(input_data.context)
            else:
                result = {"message": "Unknown task type"}
            
            return AgentOutput(
                success=True,
                result=result,
                metadata={"task_type": task_type}
            )
        except Exception as e:
            self._log(f"Calendar operation failed: {str(e)}", "error")
            return AgentOutput(
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _find_available_slots(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Find available time slots for interview"""
        
        # Mock implementation - in production, integrate with Google Calendar API
        duration_minutes = context.get('duration_minutes', 60)
        interviewer_availability = context.get('interviewer_availability', [])
        candidate_preferences = context.get('candidate_preferences', [])
        
        # Generate some time slots (mock)
        now = datetime.now(timezone.utc)
        slots = []
        
        for i in range(1, 8):  # Next 7 days
            day = now + timedelta(days=i)
            if day.weekday() < 5:  # Monday to Friday
                # Morning slot
                morning = day.replace(hour=10, minute=0, second=0, microsecond=0)
                slots.append({
                    "start": morning.isoformat(),
                    "end": (morning + timedelta(minutes=duration_minutes)).isoformat(),
                    "score": 0.9
                })
                
                # Afternoon slot
                afternoon = day.replace(hour=14, minute=0, second=0, microsecond=0)
                slots.append({
                    "start": afternoon.isoformat(),
                    "end": (afternoon + timedelta(minutes=duration_minutes)).isoformat(),
                    "score": 0.85
                })
        
        # Use AI to rank slots
        ranked_slots = await self._rank_time_slots(slots, context)
        
        return {
            "available_slots": ranked_slots[:5],  # Top 5 slots
            "total_found": len(slots)
        }
    
    async def _rank_time_slots(self, slots: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use AI to rank time slots based on preferences"""
        
        messages = [
            {
                "role": "system",
                "content": """You are a smart scheduling assistant. Rank time slots based on:
                1. Candidate time zone and preferences
                2. Interviewer availability
                3. Best interview times (usually mid-morning or early afternoon)
                4. Avoid early morning or late evening slots
                
                Return the slots array sorted by preference with updated scores.
                """
            },
            {
                "role": "user",
                "content": f"""Rank these time slots:
                
                Slots: {json.dumps(slots, indent=2)}
                
                Context: {json.dumps(context, indent=2)}
                
                Return JSON: {{"ranked_slots": [...sorted slots with scores...]}}
                """
            }
        ]
        
        try:
            result = await self._call_llm_json(messages, temperature=0.3)
            return result.get('ranked_slots', slots)
        except:
            # Fallback to original order if AI fails
            return sorted(slots, key=lambda x: x.get('score', 0), reverse=True)
    
    async def _resolve_conflict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve scheduling conflicts"""
        
        conflict_description = context.get('conflict_description', '')
        
        messages = [
            {
                "role": "system",
                "content": """You are a scheduling conflict resolver. Analyze conflicts and suggest solutions.
                
                Return JSON:
                {
                  "conflict_type": "type of conflict",
                  "suggested_action": "what to do",
                  "alternative_slots": ["suggested times"],
                  "notify_parties": ["who to notify"]
                }
                """
            },
            {
                "role": "user",
                "content": f"""Resolve this scheduling conflict:
                
                {conflict_description}
                
                Context: {json.dumps(context, indent=2)}
                """
            }
        ]
        
        result = await self._call_llm_json(messages, temperature=0.5)
        return result
