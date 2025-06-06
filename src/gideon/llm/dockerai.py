from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from .base import BaseLLMService
from ..core.config import settings


class AiDockerModelService(BaseLLMService):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        self.llm = ChatOpenAI(
            model=self.config.get("model", settings.DEFAULT_LLM_CONFIG["model"]),
            base_url="http://127.0.0.1:12434/engines/v1",
            temperature=self.config.get("temperature", settings.DEFAULT_LLM_CONFIG["temperature"]),
            api_key="ignored"
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
