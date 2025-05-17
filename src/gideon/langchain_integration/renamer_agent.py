from typing import Any, Dict, Optional

from rich.console import Console
from langchain_core.prompts import PromptTemplate

from .llm_services.factory import LLMServiceFactory, LLMServiceType
from .output_parsers import CleanJsonOutputParser


class DocumentInfo:
    def __init__(self, authors: str, year: str, title: str, topic: str):
        self.authors = authors
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
            """,
        )
        self.json_parser = CleanJsonOutputParser()

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

            return DocumentInfo(
                authors=str(result.get("authors", "")),
                year=str(result.get("year", "")),
                title=str(result.get("title", "")),
                topic=str(result.get("topic", "")),
            )

        except Exception as e:
            console.print(f"[red]Error analyzing document: {str(e)}[/]")
            return None

    def generate_filename(self, doc_info: DocumentInfo) -> str:
        """Generate a filename from document info."""
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

    def _format_authors(self, authors_str: str) -> str:
        if not authors_str:
            return "UnknownAuthor"
        authors_list = eval(authors_str)

        if len(authors_list) > 1:
            first_author = self._to_camel_case(authors_list[0])
            return f"{first_author}AndOthers"
        elif len(authors_list) == 1:
            return self._to_camel_case(authors_list[0])
        else:
            return "UnknownAuthor"

    def _format_year(self, year: str) -> str:
        if not year:
            return "UnknownYear"
        return year

    def _format_title(self, title: str) -> str:
        return self._to_camel_case(title) if title else "UnknownTitle"

    def _format_topic(self, topic: str) -> str:
        return self._to_camel_case(topic) if topic else "UnknownTopic"

    @staticmethod
    def _to_camel_case(name: str) -> str:
        words = name.split()
        return "".join(word.capitalize() for word in words)


rename_wizard = RenameWizard()
