from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..llm.base import BaseLLMService
from ..core.config import settings


class BaseAgent(ABC):
    
    def __init__(
        self,
        llm_service: Optional[BaseLLMService] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.llm_service = llm_service
        self.config = config or {}
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        pass 