from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any, List
import json

class ResumeParserAgent(BaseAgent):
    """Agent for parsing resumes and evaluating candidates"""
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Parse resume and evaluate candidate fit"""
        self._log(f"Parsing resume for candidate")
        
        try:
            # Parse resume content
            parsed_data = await self._parse_resume(input_data.context.get('resume_text', ''))
            
            # Evaluate candidate if job description is provided
            evaluation = None
            if 'job_description' in input_data.context:
                evaluation = await self._evaluate_candidate(
                    parsed_data,
                    input_data.context['job_description'],
                    input_data.context.get('questionnaire_answers', []),
                    input_data.context.get('company_values', [])
                )
            
            result = {
                "parsed_resume": parsed_data,
                "evaluation": evaluation
            }
            
            return AgentOutput(
                success=True,
                result=result,
                metadata={"parsed": True}
            )
        except Exception as e:
            self._log(f"Resume parsing failed: {str(e)}", "error")
            return AgentOutput(
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume into structured data"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert resume parser. Extract structured information from resumes.
                
                Return JSON with:
                {
                  "work_experience": [
                    {
                      "company": "Company Name",
                      "title": "Job Title",
                      "start_date": "YYYY-MM or description",
                      "end_date": "YYYY-MM or description or null",
                      "is_current": true/false,
                      "description": "brief description"
                    }
                  ],
                  "education": [
                    {
                      "institution": "University Name",
                      "degree": "Degree Type",
                      "field_of_study": "Field",
                      "graduation_year": year or null
                    }
                  ],
                  "skills": ["skill1", "skill2"],
                  "certifications": ["cert1", "cert2"],
                  "summary": "brief professional summary"
                }
                """
            },
            {
                "role": "user",
                "content": f"Parse this resume:\n\n{resume_text}"
            }
        ]
        
        result = await self._call_llm_json(messages, temperature=0.3)
        return result
    
    async def _evaluate_candidate(self, parsed_resume: Dict[str, Any], job_description: Dict[str, Any], 
                                  questionnaire_answers: List[Dict[str, Any]], company_values: List[str]) -> Dict[str, Any]:
        """Evaluate candidate fit for the job"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert candidate evaluator. Analyze candidates objectively and provide detailed assessments.
                
                Evaluate the candidate on:
                1. Skills match (0-100)
                2. Experience relevance (0-100)
                3. Education fit (0-100)
                4. Career trajectory (0-100)
                5. Questionnaire responses (0-100)
                
                Return JSON:
                {
                  "overall_score": 0-100,
                  "score_breakdown": {
                    "skills_match": 0-100,
                    "experience_relevance": 0-100,
                    "education_fit": 0-100,
                    "career_trajectory": 0-100,
                    "questionnaire_score": 0-100
                  },
                  "summary": "2-3 sentence evaluation summary",
                  "strengths": ["strength1", "strength2"],
                  "concerns": ["concern1", "concern2"],
                  "recommendation": "strong_match" or "consider" or "not_a_fit"
                }
                """
            },
            {
                "role": "user",
                "content": f"""Evaluate this candidate:
                
                CANDIDATE RESUME:
                {json.dumps(parsed_resume, indent=2)}
                
                JOB DESCRIPTION:
                {json.dumps(job_description, indent=2)}
                
                QUESTIONNAIRE ANSWERS:
                {json.dumps(questionnaire_answers, indent=2)}
                
                COMPANY VALUES:
                {json.dumps(company_values, indent=2)}
                """
            }
        ]
        
        result = await self._call_llm_json(messages, temperature=0.5)
        return result
