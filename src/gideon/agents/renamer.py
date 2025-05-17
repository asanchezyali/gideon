from typing import Optional, List, Dict, Any
from pathlib import Path
from rich.console import Console
from langchain_core.prompts import PromptTemplate

from ..llm.factory import LLMServiceFactory, LLMServiceType
from ..utils.parsers import CleanJsonOutputParser
from ..core.config import settings


class DocumentInfo:

    def __init__(self, authors: List[str], year: str, title: str, topic: str):
        self.authors = authors
        self.year = year
        self.title = title
        self.topic = topic


class RenameWizard:

    def __init__(
        self,
        service_type: LLMServiceType = LLMServiceType.OLLAMA,
        service_config: Optional[Dict[str, Any]] = None,
    ):
        self.llm_service = LLMServiceFactory.create(service_type, service_config)
        self.console = Console()
        self.json_parser = CleanJsonOutputParser()
        self.analysis_prompt = PromptTemplate.from_template(
            """
            +++SchemaOutput(format=json, schema=strict)
            +++Precision(level=high)
            +++RuleFollowing(priority=absolute)
            +++ExtractMetadata(fields=authors,year,title,topic)
            +++ArrayOutput(field=authors)
            +++DirectResponse(style=json_only)
            
            You are a document analysis expert. Extract key information from the document content.
            
            Return a JSON object with exactly these fields:
            {{
                "authors": ["Author Name 1", "Author Name 2"],
                "year": "YYYY",
                "title": "Document Title",
                "topic": "Main Topic"
            }}
            
            Rules:
            1. Authors must be an array of names
               - Include all authors you can identify
               - Use the original capitalization and format from the document
               - If no authors found, return an empty array []
            2. Year must be exactly 4 digits or empty string if not found
            3. Title should maintain its original formatting (as found in the document)
            4. Topic must be selected from this predefined list:
               - Mathematics
               - Topology
               - Geometry
               - Algebra
               - Analysis
               - Probability
               - Statistics
               - Combinatorics
               - Computer Science
               - Physics
               - Quantum Physics
               - Quantum Computing
               - Quantum Information
               - Quantum Entanglement
               - Quantum Teleportation
               - Quantum Cryptography
               - Chemistry
               - Biology
               - Economics
               - Business
               - Engineering
               - Medicine
               - Psychology
               - Philosophy
               - History
               - Literature
               - Arts
               - Social Sciences
               - Environmental Science
               - Law
               - Education
               - Marketing
               - Finance
               - Accounting
               - Management
               - Information Systems
               - Artificial Intelligence
               - Machine Learning
               - Other
               Choose the SINGLE most appropriate topic from this list that best matches the document content.
               If uncertain, choose "Other".
            5. If any field except authors is not found, return an empty string for that field
            6. All strings must use double quotes
            7. Return only the JSON object, no other text
            8. DO NOT include any <think> tags or intermediate reasoning in your output
            9. DO NOT include any troubleshooting URLs or error messages
            10. Return ONLY the valid JSON object and nothing else

            Document:
            {content}
            """
        )

    async def analyze_document(self, content: str, original_name: str) -> Optional[DocumentInfo]:
        try:
            self.console.print(f"[yellow]Analyzing document: {original_name}[/]")
            chain = await self.llm_service.create_chain(
                prompt_template=self.analysis_prompt, output_parser=self.json_parser
            )
            result = await chain.ainvoke({"content": content[: settings.MAX_CONTENT_LENGTH]})

            if not result or not isinstance(result, dict):
                self.console.print("[red]Invalid response format from LLM[/]")
                return None

            return DocumentInfo(
                authors=result.get("authors", []),
                year=str(result.get("year", "")),
                title=str(result.get("title", "")),
                topic=str(result.get("topic", "")),
            )

        except Exception as e:
            self.console.print(f"[red]Error analyzing document: {str(e)}[/]")
            return None

    def generate_filename(self, doc_info: DocumentInfo) -> str:
        filename_parts = []

        authors_str = self._format_authors(doc_info.authors)
        filename_parts.append(authors_str)

        year_str = self._format_year(doc_info.year)
        filename_parts.append(year_str)

        title_str = self._format_title(doc_info.title)
        filename_parts.append(title_str)

        topic_str = self._format_topic(doc_info.topic)
        filename_parts.append(topic_str)

        return "_".join(filename_parts) + ".pdf"

    def _format_authors(self, authors: List[str]) -> str:
        if not authors:
            return "UnknownAuthor"

        if len(authors) > 1:
            first_author = self._to_camel_case(authors[0])
            return f"{first_author}AndOthers"
        else:
            return self._to_camel_case(authors[0])

    def _format_year(self, year: str) -> str:
        return year if year else "UnknownYear"

    def _format_title(self, title: str) -> str:
        return self._to_camel_case(title) if title else "UnknownTitle"

    def _format_topic(self, topic: str) -> str:
        return self._to_camel_case(topic) if topic else "UnknownTopic"

    @staticmethod
    def _to_camel_case(text: str) -> str:
        words = text.split()
        return "".join(word.capitalize() for word in words)
