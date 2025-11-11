"""Anthropic LLM Service implementation."""

from typing import Any, Dict, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import RunnableSequence

from .base import BaseLLMService
from ..core.config import settings


class AnthropicService(BaseLLMService):
    """
    Anthropic LLM Service using Claude models.

    Supports:
    - Claude 3.5 Sonnet
    - Claude 3 Opus
    - Claude 3 Sonnet
    - Claude 3 Haiku

    Features:
    - Excellent reasoning capabilities
    - Large context windows (200K tokens)
    - Strong coding abilities
    - Great for complex analysis
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        # Get API key from config or environment
        api_key = self.config.get("api_key") or settings.ANTHROPIC_API_KEY

        if not api_key:
            raise ValueError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY in environment "
                "or pass it in config."
            )

        self.llm = ChatAnthropic(
            model=self.config.get("model", "claude-3-5-sonnet-20241022"),
            temperature=self.config.get("temperature", 0.1),
            api_key=api_key,
            max_tokens=self.config.get("max_tokens", 4096),
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
