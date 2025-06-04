from typing import Optional, List, Dict, Any
from rich.console import Console
from langchain_core.prompts import PromptTemplate
from datetime import datetime
import re
from ..llm.factory import LLMServiceFactory, LLMServiceType
from ..utils.parsers import CleanJsonOutputParser
from ..core.config import settings

UNKNOWN_AUTHOR = "Unknown_Author"
UNKNOWN_TITLE = "Unknown_Title"


class DocumentInfo:
    def __init__(self, authors: List[str], year: str, title: str, topic: str):
        self.authors = authors
        self.year = year
        self.title = title
        self.topic = topic


class RenameWizard:
    def __init__(
        self,
        llm_service_type: LLMServiceType = settings.DEFAULT_LLM_SERVICE_TYPE,
        service_config: Optional[Dict[str, Any]] = None,
    ):
        self.llm_service = LLMServiceFactory.create(llm_service_type, service_config)
        self.console = Console()
        self.json_parser = CleanJsonOutputParser()
        self.prompt = PromptTemplate.from_template(
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
            }}            
            # Rules:
            1. Authors must be an array of names
               - Include all authors you can identify
               - Use the original capitalization and format from the document
               - If no authors found, return an empty array []
            2. Year must be exactly 4 digits or empty string if not found
            3. Title should maintain its original formatting (as found in the document)
            5. If any field except authors is not found, return an empty string for that field
            6. All strings must use double quotes
            7. Return only the JSON object, no other text
            8. DO NOT include any <think> tags or intermediate reasoning in your output
            9. DO NOT include any troubleshooting URLs or error messages
            10. Return ONLY the valid JSON object and nothing else

            Document content:
            {metadata}
            {content}
            """
        )

    async def rename_document(self, content: str, original_name: str) -> Optional[DocumentInfo]:
        try:
            self.console.print(f"[yellow]Analyzing document: {original_name}[/]")
            chain = await self.llm_service.create_chain(prompt_template=self.prompt, output_parser=self.json_parser)
            result = await chain.ainvoke(
                {
                    "content": content[: settings.MAX_CONTENT_LENGTH],
                }
            )

            if not result or not isinstance(result, dict):
                self.console.print("[red]Invalid response format from LLM[/]")
                return None

            return DocumentInfo(
                authors=result.get("authors", []),
                year=str(result.get("year", "")),
                title=str(result.get("title", UNKNOWN_TITLE)) or UNKNOWN_TITLE,
            )

        except Exception as e:
            self.console.print(f"[red]Error analyzing document: {str(e)}[/]")
            return None

    def generate_filename(self, doc_info: DocumentInfo) -> str:
        filename_parts = []

        authors_str = self._format_authors(doc_info.authors)
        filename_parts.append(authors_str)

        year_str = self._format_year(doc_info.year)
        if year_str:
            filename_parts.append(year_str)

        title_str = self._format_title(doc_info.title)
        filename_parts.append(title_str)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_parts.append(timestamp)

        return ".".join(filename_parts) + ".pdf"

    def _format_authors(self, authors: List[str]) -> str:
        if not authors:
            return UNKNOWN_AUTHOR

        if len(authors) > 1:
            # Remove special characters from first author name before formatting
            first_author = re.sub(r"[^\w\s]", "", authors[0])
            # Capitalize each word and join with underscores
            formatted_author = "_".join(word.capitalize() for word in first_author.split())
            return f"{formatted_author}_And_Others"
        else:
            # Remove special characters from single author name
            clean_author = re.sub(r"[^\w\s]", "", authors[0])
            # Capitalize each word and join with underscores
            formatted_author = "_".join(word.capitalize() for word in clean_author.split())
            return formatted_author

    def _format_year(self, year: str) -> str:
        return year[:4] if year else ""

    def _format_title(self, title: str) -> str:
        if not title:
            return UNKNOWN_TITLE
        # Remove special characters except underscores
        clean_title = re.sub(r"[^\w\s]", "", title)
        # Convert to lowercase except first word and replace spaces with underscores
        words = clean_title.lower().split()
        if words:
            words[0] = words[0].capitalize()
        formatted_title = "_".join(words)
        return formatted_title
