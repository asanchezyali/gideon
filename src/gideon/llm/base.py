from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser


class BaseLLMService(ABC):
    """Base class for LLM services."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the LLM service.
        
        Args:
            config: Configuration dictionary for the LLM
        """
        self.config = config or {}
    
    @abstractmethod
    async def create_chain(
        self,
        prompt_template: PromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
    ):
        """Create a LangChain chain with the given prompt template and output parser.
        
        Args:
            prompt_template: The prompt template to use
            output_parser: Optional output parser for the LLM response
            
        Returns:
            A LangChain chain
        """
        pass 