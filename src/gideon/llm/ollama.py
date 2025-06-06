from typing import Any, Dict, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import RunnableSequence

from .base import BaseLLMService
from ..core.config import settings


class OllamaService(BaseLLMService):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        self.llm = ChatOllama(
            model=self.config.get("model", settings.DEFAULT_LLM_CONFIG["model"]),
            temperature=self.config.get("temperature", settings.DEFAULT_LLM_CONFIG["temperature"]),
        )

    async def create_chain(
        self,
        prompt: PromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
    ) -> RunnableSequence:
        chain = prompt | self.llm
        if output_parser:
            chain = chain | output_parser
        return chain
