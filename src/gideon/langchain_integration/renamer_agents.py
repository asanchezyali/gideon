from typing import Any, Dict, Optional

from rich.console import Console
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from .llm_services.factory import LLMServiceFactory, LLMServiceType


class DocumentInfo:
    def __init__(self, author: str, year: str, title: str, topic: str):
        self.author = author
        self.year = year
        self.title = title
        self.topic = topic


console = Console()


class RenameWizard:
    def __init__(
        self,
        service_type: LLMServiceType = LLMServiceType.OLLAMA,
        service_config: Optional[Dict[str, Any]] = None,
    ):
        self.llm_service = LLMServiceFactory.create(service_type, service_config or dict())
        self.output_schema = {
            "type": "object",
            "properties": {
                "author": {"type": "string"},
                "year": {"type": "string"},
                "title": {"type": "string"},
                "topic": {"type": "string"},
            },
            "required": ["author", "year", "title", "topic"],
        }
        self.analysis_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                        +++SchemaOutput(format=json, schema=strict)
                        +++Precision(level=high)
                        +++RuleFollowing(priority=absolute)
                        +++ExtractMetadata(fields=author,year,title,topic)
                        
                        You are a document analysis expert. Extract key information from the document content.
                        
                        Return a JSON object with exactly these fields:
                        {
                            "author": "AuthorName",
                            "year": "YYYY",
                            "title": "DocumentTitle",
                            "topic": "MainTopic"
                        }
                        
                        Rules:
                        1. Author must be a single capitalized name (use first author if multiple)
                        2. Year must be exactly 4 digits or empty string if not found
                        3. Title must be a single capitalized name (use first title if multiple)
                        4. Topic must be a single capitalized name (use first topic if multiple)
                        5. If any field is not found, return an empty string for that field
                        6. All strings must use double quotes
                        7. Return only the JSON object, no other text
                    """,
                ),
                ("human", "{content}"),
            ]
        )
        self.json_parser = JsonOutputParser()

    async def analyze_document(self, content: str, original_name: str) -> Optional[DocumentInfo]:
        try:
            console.print(f"[yellow]Analyzing document: {original_name}[/]")

            chain = await self.llm_service.create_chain(
                prompt_template=self.analysis_prompt, output_parser=self.json_parser
            )

            result = await chain.ainvoke({"content": content[:5000]})

            if not result or not isinstance(result, dict):
                console.print("[red]Invalid response format from LLM[/]")
                return None

            console.print(f"[green]Analysis result: {result}[/]")

            return DocumentInfo(
                author=str(result.get("author", "")),
                year=str(result.get("year", "")),
                title=str(result.get("title", "")),
                topic=str(result.get("topic", "")),
            )

        except Exception as e:
            console.print(f"[red]Error analyzing document: {str(e)}[/]")
            return None

    def generate_filename(self, doc_info: DocumentInfo) -> str:
        """Generate a standardized filename from document information."""
        return f"{doc_info.author}.{doc_info.year}.{doc_info.title}.{doc_info.topic}.pdf"


rename_wizard = RenameWizard()
