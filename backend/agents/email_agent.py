from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any
import json

class EmailAgent(BaseAgent):
    """Agent for composing personalized emails to candidates"""
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Compose an email based on context"""
        self._log(f"Composing email: {input_data.context.get('email_type', 'unknown')}")
        
        try:
            email_content = await self._compose_email(input_data.context)
            
            return AgentOutput(
                success=True,
                result=email_content,
                metadata={"email_type": input_data.context.get('email_type')}
            )
        except Exception as e:
            self._log(f"Email composition failed: {str(e)}", "error")
            return AgentOutput(
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _compose_email(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compose personalized email content"""
        
        email_type = context.get('email_type', 'confirmation')
        tone = context.get('tone', 'professional')
        candidate_name = context.get('candidate_name', 'Candidate')
        company_name = context.get('company_name', 'Our Company')
        job_title = context.get('job_title', 'the position')
        persona = context.get('persona', {})
        signature = context.get('signature', f'Best regards,\nThe {company_name} Team')
        
        # Build system prompt based on email type
        system_prompts = {
            'confirmation': f"""You are writing an application confirmation email. Be professional and encouraging.
            Acknowledge the candidate's application and set expectations for next steps.
            Tone: {tone}""",
            
            'shortlisted': f"""You are writing an email to a shortlisted candidate. Be enthusiastic and professional.
            Explain why they stood out and what the next steps are.
            Tone: {tone}""",
            
            'rejected': f"""You are writing a rejection email. Be empathetic, respectful, and encouraging.
            Thank them for their time, provide constructive feedback if available, and wish them well.
            Tone: empathetic and professional""",
            
            'interview_invite': f"""You are writing an interview invitation email. Be clear, professional, and welcoming.
            Provide all necessary details and make the candidate feel valued.
            Tone: {tone}""",
            
            'offer': f"""You are writing a job offer email. Be congratulatory and professional.
            Express excitement about having them join the team.
            Tone: professional and warm"""
        }
        
        system_prompt = system_prompts.get(email_type, system_prompts['confirmation'])
        
        # Build user prompt with context
        user_prompt = f"""Compose an email for:
        
        Email Type: {email_type}
        Candidate Name: {candidate_name}
        Company: {company_name}
        Job Title: {job_title}
        
        Additional Context:
        {json.dumps(context.get('additional_context', {}), indent=2)}
        
        Company Persona:
        {json.dumps(persona, indent=2)}
        
        Return JSON:
        {{
          "subject": "email subject line",
          "body": "email body (use \\n for line breaks)",
          "preview_text": "first 50 characters for preview"
        }}
        
        Do not include signature in body - it will be added separately.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        result = await self._call_llm_json(messages, temperature=0.7)
        
        # Add signature
        result['body'] = result['body'] + f"\n\n{signature}"
        
        return result
