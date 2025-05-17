from typing import Any, Dict, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import RunnableSequence
from langchain.chains import LLMChain

from .base import BaseLLMService
from ..core.config import settings


class OllamaService(BaseLLMService):
    """Service for interacting with Ollama LLM."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Ollama service.
        
        Args:
            config: Configuration for the Ollama service
        """
        super().__init__(config)

        self.llm = ChatOllama(
            model=self.config.get("model", settings.DEFAULT_LLM_CONFIG["model"]),
            temperature=self.config.get("temperature", settings.DEFAULT_LLM_CONFIG["temperature"]),
        )
    
    async def create_chain(
        self,
        prompt_template: PromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
    ) -> RunnableSequence:
        """Create a LangChain chain with Ollama.
        
        Args:
            prompt_template: The prompt template to use
            output_parser: Optional output parser for the LLM response
            
        Returns:
            A configured LangChain chain
        """
        chain = prompt_template | self.llm
        if output_parser:
            chain = chain | output_parser
        return chain
