from typing import Dict, Any, Optional
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

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
    
    def __init__(self):
        self.llm = OllamaLLM(model="llama3.1")
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a document analysis expert. Extract key information from the document content.
            
            Return a JSON object with exactly these fields:
            {{
                "author": "AuthorName",
                "year": "YYYY",
                "title": "DocumentTitle",
                "topic": "MainTopic"
            }}
            
            Rules:
            1. Author must be a single capitalized name (use first author if multiple)
            2. Year must be exactly 4 digits (use "Unknown" if not found)
            3. Title must be in camelCase without spaces (e.g., "GeometricRelationsInAnArbitraryMetricSpace")
            4. Topic must be in camelCase (e.g., "DifferentialGeometry")
            5. All strings must be in double quotes
            6. No comments or explanations
            
            Example:
            {{
                "author": "Schuller",
                "year": "2013",
                "title": "GeometricAnatomyTheoreticalPhysics",
                "topic": "DifferentialGeometry"
            }}"""),
            ("user", "Analyze this document: {content}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text response."""
        try:
            console.print(f"\n[bold blue]Model Response:[/bold blue]")
            console.print(Panel(text, title="Raw Response", border_style="blue"))
            
            # Find JSON-like content
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if not match:
                console.print("[red]No JSON object found in response[/red]")
                return None
                
            # Clean up the match
            json_str = match.group(0)
            json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)  # Remove comments
            json_str = re.sub(r'\s+', ' ', json_str)  # Normalize whitespace
            
            console.print(f"\n[bold green]Extracted JSON:[/bold green]")
            console.print(Panel(json_str, title="Parsed JSON", border_style="green"))
            return json.loads(json_str)
        except Exception as e:
            console.print(f"[red]Error extracting JSON: {str(e)}[/red]")
            return None
    
    def _normalize_author(self, text: str) -> str:
        """Normalize author name by removing accents and ensuring proper capitalization."""
        # Remove accents and special characters
        text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i')
        text = text.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        text = text.replace('ü', 'u').replace('ö', 'o').replace('ä', 'a')
        text = text.replace('ë', 'e').replace('ï', 'i').replace('ÿ', 'y')
        text = text.replace('ç', 'c').replace('ß', 'ss')
        
        # Remove any remaining special characters
        text = re.sub(r'[^a-zA-Z0-9]', '', text)
        
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
        
        # Remove any remaining special characters except letters and numbers
        text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
        
        # Split into words and capitalize each word
        words = text.split()
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
            if not analysis["author"]:
                analysis["author"] = "UnknownAuthor"
            else:
                # Take first author if multiple
                author = analysis["author"].split("_")[0].split()[0]
                if not author:
                    analysis["author"] = "UnknownAuthor"
                else:
                    analysis["author"] = self._normalize_author(author)
            
            if not analysis["year"] or analysis["year"].lower() in ["null", "n/a", "unknown"]:
                analysis["year"] = "Unknown"
            elif not re.match(r'^\d{4}$', str(analysis["year"])):
                console.print(f"[yellow]Invalid year format: {analysis['year']}. Using 'Unknown'[/yellow]")
                analysis["year"] = "Unknown"
            
            if not analysis["title"]:
                analysis["title"] = "UntitledDocument"
            else:
                analysis["title"] = self._normalize_camelcase(analysis["title"])
            
            if not analysis["topic"]:
                analysis["topic"] = "General"
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
            
            # Get response from LLM
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing document...", total=None)
                result = await self.chain.ainvoke({"content": content[:5000]})
                progress.update(task, completed=True)
            
            # Extract and validate JSON
            analysis = self._extract_json(result)
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