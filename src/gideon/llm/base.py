from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser


class BaseLLMService(ABC):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    async def create_chain(
        self,
        prompt: PromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
    ):
        pass
