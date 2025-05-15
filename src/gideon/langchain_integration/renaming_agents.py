"""Document renaming agent using LLM services."""
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from .llm_services.factory import LLMServiceFactory, LLMServiceType

# Configure rich console
console = Console()

class DocumentInfo:
    """Information extracted from a document."""
    def __init__(self, author: str, year: str, title: str, topic: str):
        self.author = author
        self.year = year
        self.title = title
        self.topic = topic

class RenamingAgent:
    """Agent that analyzes documents and generates standardized filenames."""
    
    def __init__(
        self,
        service_type: LLMServiceType = LLMServiceType.OLLAMA,
        service_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the renaming agent with configurable LLM service."""
        self.llm_service = LLMServiceFactory.create(service_type, service_config or {})
        
        # Define output schema for the parser
        self.output_schema = {
            "type": "object",
            "properties": {
                "author": {"type": "string"},
                "year": {"type": "string"},
                "title": {"type": "string"},
                "topic": {"type": "string"}
            },
            "required": ["author", "year", "title", "topic"]
        }
        
        # Define the document analysis prompt template
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a document analysis expert. Extract key information from the document content. \
Return a JSON object with metadata.

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
3. Title must be in camelCase without spaces
4. Topic must be a single word in camelCase describing the main subject
5. All strings must use double quotes
6. Return only the JSON object, no other text"""),
            ("human", "{content}")
        ])
        
        # Create output parser for JSON responses
        self.json_parser = JsonOutputParser()
    
    def _normalize_author(self, text: str) -> str:
        """Normalize author name by removing accents and ensuring proper capitalization."""
        # Remove accents and special characters
        text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i')
        text = text.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        text = text.replace('ü', 'u').replace('ö', 'o').replace('ä', 'a')
        text = text.replace('ë', 'e').replace('ï', 'i').replace('ÿ', 'y')
        text = text.replace('ç', 'c').replace('ß', 'ss')
        
        # Remove any remaining special characters
        text = ''.join(c for c in text if c.isalnum())
        
        # Ensure first letter is uppercase
        if text:
            text = text[0].upper() + text[1:]
        return text
    
    def _normalize_camelcase(self, text: str) -> str:
        """Convert text to camelCase while preserving existing camelCase."""
        # Remove accents and special characters
        text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i')
        text = text.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        text = text.replace('ü', 'u').replace('ö', 'o').replace('ä', 'a')
        text = text.replace('ë', 'e').replace('ï', 'i').replace('ÿ', 'y')
        text = text.replace('ç', 'c').replace('ß', 'ss')
        
        # Split into words
        words = ''.join(c for c in text if c.isalnum() or c.isspace()).split()
        if not words:
            return ""
            
        # If text is already in camelCase, preserve it
        if any(c.isupper() for c in text[1:]):
            return text
            
        # Convert to camelCase
        result = words[0].lower()
        for word in words[1:]:
            result += word.capitalize()
        return result
    
    def _validate_analysis(self, analysis: Dict[str, Any]) -> bool:
        """Validate the extracted information."""
        try:
            # Check required fields
            required = {"author", "year", "title", "topic"}
            if not all(field in analysis for field in required):
                missing = required - set(analysis.keys())
                console.print(f"[red]Missing required fields: {', '.join(missing)}[/red]")
                return False
            
            # Normalize and validate values
            if not analysis["author"] or analysis["author"].strip() == "":
                analysis["author"] = "UnknownAuthor"
                console.print("[yellow]No author found. Using 'UnknownAuthor'[/yellow]")
            else:
                author = analysis["author"].split("_")[0].split()[0]
                if not author:
                    analysis["author"] = "UnknownAuthor"
                else:
                    analysis["author"] = self._normalize_author(author)
            
            if not analysis["year"] or not analysis["year"].strip().isdigit():
                analysis["year"] = "Unknown"
                console.print("[yellow]No valid year found. Using 'Unknown'[/yellow]")
            
            if not analysis["title"] or analysis["title"].strip() == "":
                analysis["title"] = "UntitledDocument"
                console.print("[yellow]No title found. Using 'UntitledDocument'[/yellow]")
            else:
                analysis["title"] = self._normalize_camelcase(analysis["title"])
            
            if not analysis["topic"] or analysis["topic"].strip() == "":
                analysis["topic"] = "General"
                console.print("[yellow]No topic found. Using 'General'[/yellow]")
            else:
                analysis["topic"] = self._normalize_camelcase(analysis["topic"])
            
            console.print("\n[bold green]Validation Results:[/bold green]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            for field, value in analysis.items():
                table.add_row(field, str(value))
            console.print(table)
            
            return True
        except Exception as e:
            console.print(f"[red]Error validating analysis: {str(e)}[/red]")
            return False
    
    async def analyze_document(self, content: str, original_name: str) -> Optional[DocumentInfo]:
        """Analyze document content and extract key information."""
        try:
            console.print(f"\n[bold yellow]Analyzing file: {original_name}[/bold yellow]")
            
            # Create chain with output parser
            chain = await self.llm_service.create_chain(
                self.analysis_prompt,
                self.json_parser
            )
            
            # Process document
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing document...", total=None)
                analysis = await chain.ainvoke({"content": content[:5000]})
                progress.update(task, completed=True)
            
            # Validate and normalize results
            if not analysis or not self._validate_analysis(analysis):
                return None
            
            return DocumentInfo(
                author=analysis["author"],
                year=analysis["year"],
                title=analysis["title"],
                topic=analysis["topic"]
            )
            
        except Exception as e:
            console.print(f"[red]Error in analysis: {str(e)}[/red]")
            return None
    
    def generate_filename(self, doc_info: DocumentInfo) -> str:
        """Generate a standardized filename from document information."""
        return f"{doc_info.author}.{doc_info.year}.{doc_info.title}.{doc_info.topic}.pdf"

# Create a singleton instance of the agent
renaming_agent = RenamingAgent()