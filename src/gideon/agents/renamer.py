from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Protocol
from rich.console import Console
from langchain_core.prompts import PromptTemplate
from datetime import datetime
import re
from ..llm.factory import LLMServiceFactory, LLMServiceType
from ..utils.parsers import CleanJsonOutputParser
from ..core.config import settings

UNKNOWN_AUTHOR = "Unknown_Author"
UNKNOWN_TITLE = "Unknown_Title"


@dataclass
class DocumentInfo:
    authors: List[str]
    year: str
    title: str


class Logger(Protocol):
    """Protocol defining logging interface."""

    def log(self, message: str) -> None:
        """Log a message."""
        ...


class ConsoleLogger:
    """Implementation of the Logger protocol using Rich Console."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def log(self, message: str) -> None:
        if "[red]" in message:
            self.console.print(message)
        else:
            self.console.print(message)


class DocumentAnalyzer:
    def __init__(
        self,
        llm_service_type: LLMServiceType = settings.DEFAULT_LLM_SERVICE_TYPE,
        service_config: Optional[Dict[str, Any]] = None,
        logger: Optional[Logger] = None,
    ):
        self.llm_service = LLMServiceFactory.create(llm_service_type, service_config)
        self.logger = logger or ConsoleLogger()
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
            {content}
            """
        )

    async def analyze(self, content: str, file_name: str) -> Optional[DocumentInfo]:
        try:
            self.logger.log(f"[yellow]Analyzing document: {file_name}[/]")
            chain = await self.llm_service.create_chain(prompt_template=self.prompt, output_parser=self.json_parser)
            result = await chain.ainvoke(
                {
                    "content": content[: settings.MAX_CONTENT_LENGTH],
                }
            )

            if not result or not isinstance(result, dict):
                self.logger.log("[red]Invalid response format from LLM[/]")
                return None

            return DocumentInfo(
                authors=result.get("authors", []),
                year=str(result.get("year", "")),
                title=str(result.get("title", UNKNOWN_TITLE)) or UNKNOWN_TITLE,
            )

        except Exception as e:
            self.logger.log(f"[red]Error analyzing document: {str(e)}[/]")
            return None


class FormatterInterface(Protocol):
    """Protocol defining formatter interface."""

    def format(self, doc_info: DocumentInfo) -> str:
        """Format a part of document info into a string for filename."""
        ...


class AuthorFormatter:
    def format(self, doc_info: DocumentInfo) -> str:
        """Format authors for filename."""
        authors = doc_info.authors
        if not authors:
            return UNKNOWN_AUTHOR

        if len(authors) > 1:
            first_author = re.sub(r"[^\w\s]", "", authors[0])
            formatted_author = "_".join(word.capitalize() for word in first_author.split())
            return f"{formatted_author}_And_Others"
        else:
            clean_author = re.sub(r"[^\w\s]", "", authors[0])
            formatted_author = "_".join(word.capitalize() for word in clean_author.split())
            return formatted_author

    @staticmethod
    def format_authors(authors: List[str]) -> str:
        if not authors:
            return UNKNOWN_AUTHOR

        if len(authors) > 1:
            first_author = re.sub(r"[^\w\s]", "", authors[0])
            formatted_author = "_".join(word.capitalize() for word in first_author.split())
            return f"{formatted_author}_And_Others"
        else:
            clean_author = re.sub(r"[^\w\s]", "", authors[0])
            formatted_author = "_".join(word.capitalize() for word in clean_author.split())
            return formatted_author


class TitleFormatter:
    def format(self, doc_info: DocumentInfo) -> str:
        """Format title for filename."""
        title = doc_info.title
        if not title:
            return UNKNOWN_TITLE
        clean_title = re.sub(r"[^\w\s]", "", title)
        words = clean_title.lower().split()
        if words:
            words[0] = words[0].capitalize()
        formatted_title = "_".join(words)
        return formatted_title

    @staticmethod
    def format_title(title: str) -> str:
        if not title:
            return UNKNOWN_TITLE
        clean_title = re.sub(r"[^\w\s]", "", title)
        words = clean_title.lower().split()
        if words:
            words[0] = words[0].capitalize()
        formatted_title = "_".join(words)
        return formatted_title


class YearFormatter:
    def format(self, doc_info: DocumentInfo) -> str:
        """Format year for filename."""
        return doc_info.year[:4] if doc_info.year else ""

    @staticmethod
    def format_year(year: str) -> str:
        return year[:4] if year else ""


class TimestampFormatter:
    def format(self, doc_info: DocumentInfo) -> str:
        """Format timestamp for filename."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")


class FileNameGenerator:
    def __init__(self, formatters: Optional[List[FormatterInterface]] = None):
        self.formatters = formatters or [AuthorFormatter(), YearFormatter(), TitleFormatter(), TimestampFormatter()]

    def generate_filename(self, doc_info: DocumentInfo) -> str:
        filename_parts = []

        for formatter in self.formatters:
            formatted_part = formatter.format(doc_info)
            if formatted_part:
                filename_parts.append(formatted_part)

        return ".".join(filename_parts) + ".pdf"

    @classmethod
    def from_doc_info(cls, doc_info: DocumentInfo):
        generator = cls()
        return generator.generate_filename(doc_info)


class RenameService:
    def __init__(
        self,
        document_analyzer: Optional[DocumentAnalyzer] = None,
        filename_generator: Optional[FileNameGenerator] = None,
        llm_service_type: LLMServiceType = settings.DEFAULT_LLM_SERVICE_TYPE,
        service_config: Optional[Dict[str, Any]] = None,
        logger: Optional[Logger] = None,
    ):
        """
        Initialize the rename service with dependencies.

        Args:
            document_analyzer: Optional pre-configured document analyzer
            filename_generator: Optional pre-configured filename generator
            llm_service_type: Type of LLM to use if creating a new analyzer
            service_config: Configuration for the LLM service
            logger: Optional logger for operations
        """
        self.logger = logger or ConsoleLogger()

        if document_analyzer is None:
            document_analyzer = DocumentAnalyzer(llm_service_type, service_config, self.logger)
        self.document_analyzer = document_analyzer

        self.filename_generator = filename_generator or FileNameGenerator()

    async def rename_file(self, content: str, file_name: str) -> str:
        """
        Rename a file based on its content.

        Args:
            content: The content of the file
            file_name: Current file name

        Returns:
            New file name or the original if analysis fails
        """
        doc_info = await self.document_analyzer.analyze(content, file_name)
        if not doc_info:
            return file_name

        new_name = self.filename_generator.generate_filename(doc_info)
        return new_name
