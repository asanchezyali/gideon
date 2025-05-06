from typing import Any, Dict, Optional
from rich.console import Console

from .llm_services.factory import LLMServiceFactory, LLMServiceType


class DocumentInfo:
    def __init__(self, author: str, year: str, title: str, topic: str):
        self.author = author
        self.year = year
        self.title = title
        self.topic = topic


console = Console()


class RenamerAgent:
    def __init__(
        self,
        service_type: LLMServiceType = LLMServiceType.OLLAMA,
        service_config: Optional[Dict[str, Any]] = None,
    ):
        self.llm_service = LLMServiceFactory.create(service_type, service_config or dict())

    async def analyze_document(self, content: str, original_name: str) -> Optional[DocumentInfo]:
        print(f"Analyzing document: {original_name}")


renamer_agent = RenamerAgent()