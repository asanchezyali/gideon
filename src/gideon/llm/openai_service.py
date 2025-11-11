"""OpenAI LLM Service implementation."""

from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import RunnableSequence

from .base import BaseLLMService
from ..core.config import settings


class OpenAIService(BaseLLMService):
    """
    OpenAI LLM Service using GPT models.

    Supports:
    - GPT-4 Turbo
    - GPT-4
    - GPT-3.5 Turbo

    Features:
    - Fast inference
    - High quality outputs
    - Reasonable pricing
    - Great for production use
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        # Get API key from config or environment
        api_key = self.config.get("api_key") or settings.OPENAI_API_KEY

        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY in environment "
                "or pass it in config."
            )

        self.llm = ChatOpenAI(
            model=self.config.get("model", "gpt-4-turbo-preview"),
            temperature=self.config.get("temperature", 0.1),
            api_key=api_key,
            max_tokens=self.config.get("max_tokens"),
            timeout=self.config.get("timeout", 60),
        )

    async def create_chain(
        self,
        prompt: PromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
    ) -> RunnableSequence:
        """Create LangChain runnable sequence."""
        chain = prompt | self.llm
        if output_parser:
            chain = chain | output_parser
        return chain
