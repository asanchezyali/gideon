from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..llm.base import BaseLLMService
from ..core.config import settings


class BaseAgent(ABC):
    """Base class for all Gideon agents."""
    
    def __init__(
        self,
        llm_service: Optional[BaseLLMService] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the agent.
        
        Args:
            llm_service: LLM service to use
            config: Additional configuration for the agent
        """
        self.llm_service = llm_service
        self.config = config or {}
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """Process the input according to the agent's purpose.
        
        This method should be implemented by each specific agent.
        """
        pass 