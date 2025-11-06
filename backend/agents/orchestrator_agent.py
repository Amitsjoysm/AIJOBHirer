from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any, List
import json

class OrchestratorAgent(BaseAgent):
    """Main orchestrator that routes tasks to specialized agents"""
    
    def __init__(self, groq_service):
        super().__init__(groq_service)
        self.available_agents = [
            "job_creation",
            "resume_parser",
            "email",
            "persona_creator",
            "calendar",
            "report"
        ]
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Determine which agent(s) to use for the given task"""
        self._log(f"Orchestrating task: {input_data.task}")
        
        try:
            # Analyze the task and determine the appropriate agent
            agent_decision = await self._decide_agent(input_data)
            
            return AgentOutput(
                success=True,
                result=agent_decision,
                metadata={"orchestrator": "decision_made"}
            )
        except Exception as e:
            self._log(f"Orchestration failed: {str(e)}", "error")
            return AgentOutput(
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _decide_agent(self, input_data: AgentInput) -> Dict[str, Any]:
        """Decide which agent to use based on the task"""
        
        messages = [
            {
                "role": "system",
                "content": f"""You are an intelligent orchestrator for an AI hiring system.
                
Available agents:
                - job_creation: Create job descriptions and screening questions
                - resume_parser: Parse and analyze resumes
                - email: Compose and send emails to candidates
                - persona_creator: Create company hiring persona
                - calendar: Schedule interviews and manage calendar
                - report: Generate analytics and reports
                
                Given a task, determine which agent should handle it and extract relevant parameters.
                Return JSON with: {{"agent": "agent_name", "parameters": {{}}, "reasoning": "why this agent"}}
                """
            },
            {
                "role": "user",
                "content": f"Task: {input_data.task}\n\nContext: {json.dumps(input_data.context)}"
            }
        ]
        
        decision = await self._call_llm_json(messages, temperature=0.3)
        self._log(f"Agent decision: {decision['agent']}")
        
        return decision
    
    async def decide_email_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decide what email action to take based on application status"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an email orchestrator for a hiring system.
                
                Based on the application context, decide:
                1. Should an email be sent?
                2. What type of email? (confirmation, shortlisted, rejected, interview_invite, offer)
                3. What tone to use?
                
                Return JSON: {"should_send": bool, "email_type": "type", "tone": "professional/friendly/empathetic", "reasoning": "why"}
                """
            },
            {
                "role": "user",
                "content": f"Application Context:\n{json.dumps(context, indent=2)}"
            }
        ]
        
        decision = await self._call_llm_json(messages, temperature=0.3)
        return decision
    
    async def process_chat_message(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chat message and determine appropriate response and actions"""
        
        message = context.get("message", "")
        conversation_history = context.get("conversation_history", [])
        company = context.get("company", {})
        jobs = context.get("jobs", [])
        applications = context.get("applications", [])
        
        # Build context summary
        context_summary = f"""
Company: {company.get('name', 'Not set')}
Active Jobs: {len([j for j in jobs if j.get('status') == 'active'])}
Total Applications: {len(applications)}
Recent Applications: {len([a for a in applications if a.get('status') == 'submitted'])} new
        """
        
        system_prompt = f"""You are an AI hiring assistant for HireFlow AI. You help users manage their hiring process.

Current Context:
{context_summary}

You can help with:
- Creating job descriptions
- Reviewing applications
- Scheduling interviews
- Analyzing hiring metrics
- Answering questions about candidates

Respond naturally and helpfully. If the user asks you to perform an action (like creating a job or scheduling an interview), acknowledge it and provide guidance on next steps.

For actions, include in your response:
- A helpful conversational response
- Suggested action (if any): job_creation, review_applications, schedule_interview, analytics, general_help
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-5:]:  # Last 5 messages
            messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Get response
        try:
            response_text = await self._call_llm(messages, temperature=0.7)
            
            # Determine if an action should be suggested
            action_detection_prompt = f"""Based on this user message: "{message}"
            
And assistant response: "{response_text}"

Determine if a specific action should be taken. Return JSON:
{{"action": "job_creation|review_applications|schedule_interview|analytics|general_help", "confidence": 0.0-1.0}}

Only suggest actions if the user explicitly asks for them."""
            
            action_result = await self._call_llm_json([
                {"role": "system", "content": action_detection_prompt}
            ], temperature=0.3)
            
            return {
                "response": response_text,
                "action_taken": action_result.get("action") if action_result.get("confidence", 0) > 0.7 else None,
                "data": {
                    "jobs_count": len(jobs),
                    "applications_count": len(applications)
                }
            }
        except Exception as e:
            return {
                "response": "I'm here to help you with your hiring needs! You can ask me about creating jobs, reviewing applications, scheduling interviews, or analyzing your hiring metrics.",
                "action_taken": None,
                "data": {}
            }
