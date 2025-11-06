from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any, List
import json

class JobCreationAgent(BaseAgent):
    """Agent for creating job descriptions and screening questions using AI"""
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Generate job description and screening questions"""
        self._log(f"Creating job content for: {input_data.context.get('title', 'Unknown')}")
        
        try:
            # Generate job description
            job_description = await self._generate_job_description(input_data.context)
            
            # Generate screening questions
            screening_questions = await self._generate_screening_questions(input_data.context)
            
            result = {
                "description": job_description['description'],
                "requirements": job_description['requirements'],
                "nice_to_have": job_description['nice_to_have'],
                "screening_questions": screening_questions
            }
            
            return AgentOutput(
                success=True,
                result=result,
                metadata={"ai_generated": True}
            )
        except Exception as e:
            self._log(f"Job creation failed: {str(e)}", "error")
            return AgentOutput(
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _generate_job_description(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive job description"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert job description writer. Create compelling, clear job descriptions that attract quality candidates.
                
                Return JSON with:
                {
                  "description": "detailed 2-3 paragraph job description",
                  "requirements": ["list of required qualifications"],
                  "nice_to_have": ["list of preferred qualifications"]
                }
                """
            },
            {
                "role": "user",
                "content": f"""Create a job description for:
                
                Title: {context.get('title', 'Not specified')}
                Department: {context.get('department', 'Not specified')}
                Experience Level: {context.get('experience_level', 'Not specified')}
                Job Type: {context.get('job_type', 'Not specified')}
                Location: {context.get('location_type', 'Not specified')}
                
                Additional context: {context.get('ai_input', '')}
                
                Company values: {context.get('company_values', 'Not provided')}
                """
            }
        ]
        
        result = await self._call_llm_json(messages, temperature=0.7)
        return result
    
    async def _generate_screening_questions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate screening questions tailored to the job"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert at creating effective screening questions for job candidates.
                
                Create 5-10 screening questions that assess:
                1. Technical skills and experience
                2. Cultural fit
                3. Motivation and career goals
                4. Availability and logistics
                
                Return JSON array:
                [
                  {
                    "question": "question text",
                    "question_type": "text" or "multiple_choice" or "yes_no",
                    "options": ["option1", "option2"] (only for multiple_choice),
                    "required": true/false,
                    "weight": 0.5 to 2.0 (importance weight)
                  }
                ]
                """
            },
            {
                "role": "user",
                "content": f"""Create screening questions for:
                
                Title: {context.get('title', 'Not specified')}
                Experience Level: {context.get('experience_level', 'Not specified')}
                Requirements: {context.get('requirements', [])}
                
                Additional context: {context.get('ai_input', '')}
                """
            }
        ]
        
        result = await self._call_llm_json(messages, temperature=0.7)
        return result
