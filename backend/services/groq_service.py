import aiohttp
import json
from typing import List, Dict, Any, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class GroqService:
    """Service for interacting with Groq API"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    async def complete(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Get completion from Groq API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Groq API error: {error_text}")
                        raise Exception(f"Groq API error: {error_text}")
                    
                    data = await response.json()
                    return data['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            raise
    
    async def complete_json(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """Get JSON completion from Groq API"""
        # Add instruction to return JSON
        messages[-1]['content'] += "\n\nReturn your response as valid JSON only, with no additional text."
        
        response = await self.complete(messages, temperature=temperature, max_tokens=3000)
        
        try:
            # Try to parse JSON from response
            # Sometimes the model wraps JSON in ```json ... ```
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Groq response: {response}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
