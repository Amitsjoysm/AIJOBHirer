from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class AgentInput(BaseModel):
    """Base input schema for agents"""
    task: str
    context: Dict[str, Any] = {}

class AgentOutput(BaseModel):
    """Base output schema for agents"""
    success: bool
    result: Any
    error: str = ""
    metadata: Dict[str, Any] = {}

class BaseAgent(ABC):
    """Base class for all AI agents following Parlant.io architecture"""
    
    def __init__(self, groq_service):
        self.groq_service = groq_service
        self.agent_name = self.__class__.__name__
    
    @abstractmethod
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute the agent's task"""
        pass
    
    def _log(self, message: str, level: str = "info"):
        """Log agent activity"""
        log_message = f"[{self.agent_name}] {message}"
        if level == "info":
            logger.info(log_message)
        elif level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)
    
    async def _call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Call LLM with error handling"""
        try:
            response = await self.groq_service.complete(messages, temperature=temperature)
            return response
        except Exception as e:
            self._log(f"LLM call failed: {str(e)}", "error")
            raise
    
    async def _call_llm_json(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """Call LLM expecting JSON response"""
        try:
            response = await self.groq_service.complete_json(messages, temperature=temperature)
            return response
        except Exception as e:
            self._log(f"LLM JSON call failed: {str(e)}", "error")
            raise
