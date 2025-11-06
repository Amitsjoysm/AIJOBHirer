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
