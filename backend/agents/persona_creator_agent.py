from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any
import aiohttp
from bs4 import BeautifulSoup
import json

class PersonaCreatorAgent(BaseAgent):
    """Agent for creating company hiring persona by analyzing website"""
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Create company persona from website"""
        self._log(f"Creating persona for: {input_data.context.get('company_name', 'Unknown')}")
        
        try:
            website_url = input_data.context.get('website_url')
            
            if website_url:
                # Scrape website content
                website_content = await self._scrape_website(website_url)
            else:
                website_content = "No website provided"
            
            # Generate persona
            persona = await self._generate_persona(
                company_name=input_data.context.get('company_name', ''),
                industry=input_data.context.get('industry', ''),
                description=input_data.context.get('description', ''),
                website_content=website_content
            )
            
            return AgentOutput(
                success=True,
                result=persona,
                metadata={"website_scraped": bool(website_url)}
            )
        except Exception as e:
            self._log(f"Persona creation failed: {str(e)}", "error")
            return AgentOutput(
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _scrape_website(self, url: str) -> str:
        """Scrape key content from company website"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        return "Could not fetch website content"
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text
                    text = soup.get_text()
                    
                    # Clean up text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    # Limit to first 3000 characters
                    return text[:3000]
        except Exception as e:
            self._log(f"Website scraping failed: {str(e)}", "warning")
            return "Could not fetch website content"
    
    async def _generate_persona(self, company_name: str, industry: str, description: str, website_content: str) -> Dict[str, Any]:
        """Generate company hiring persona"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert at analyzing companies and creating hiring personas.
                
                Based on the company information, create a comprehensive hiring persona that includes:
                - Company mission and values
                - Company culture
                - Hiring style and preferences
                - Communication tone
                
                Return JSON:
                {
                  "company_mission": "mission statement",
                  "company_values": ["value1", "value2", "value3"],
                  "company_culture": "description of culture",
                  "hiring_style": "description of hiring approach",
                  "tone": "professional" or "casual" or "friendly"
                }
                """
            },
            {
                "role": "user",
                "content": f"""Create a hiring persona for:
                
                Company Name: {company_name}
                Industry: {industry}
                Description: {description}
                
                Website Content:
                {website_content}
                """
            }
        ]
        
        result = await self._call_llm_json(messages, temperature=0.7)
        return result
