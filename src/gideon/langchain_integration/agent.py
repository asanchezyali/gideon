from pathlib import Path
from typing import List, Dict, Any, AsyncIterator
import asyncio
from enum import Enum
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
import warnings
from PyPDF2 import PdfReader
import io

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.vectorstores import InMemoryVectorStore

from .document_processor import DocumentProcessor
from .classifiers import DocumentClassifier, DocumentType
from ..constants import DocType

console = Console()

# Suppress PyPDF2 warnings
warnings.filterwarnings("ignore", category=UserWarning, module="PyPDF2")

class ProcessingEvent(str, Enum):
    START = "start"
    LOAD = "load"
    CLASSIFY = "classify"
    MOVE = "move"
    COMPLETE = "complete"
    ERROR = "error"

class DocumentAgent:
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.processor = DocumentProcessor()
        self.classifier = DocumentClassifier()
        self.llm = OllamaLLM(model="deepseek-coder:1.3b")
        self.embeddings = OllamaEmbeddings(model="deepseek-coder:1.3b")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.vectorstore = None
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console
        )
        self.current_file = None
        
    def _get_target_directory(self, doc_type: DocumentType) -> Path:
        """Get the appropriate target directory for a document type."""
        type_to_dir = {
            DocumentType.ARTICLE: "articles",
            DocumentType.BOOK: "books",
            DocumentType.THESIS: "theses",
            DocumentType.COMMERCIAL_DOCUMENT: "commercial",
            DocumentType.LEGAL_DOCUMENT: "legal",
            DocumentType.NON_DISCLOSURE_AGREEMENT: "nda",
            DocumentType.PERSONAL_DOCUMENT: "personal"
        }
        
        target_dir = self.directory / type_to_dir[doc_type]
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    async def _emit_event(self, 
                       event_type: ProcessingEvent, 
                       file_path: str, 
                       details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create and return an event object."""
        event = {
            "event": event_type,
            "file_path": file_path,
            "details": details or {}
        }
        return event
        
    async def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract content from PDF file with better error handling."""
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                content = []
                # Extract text from first 3 pages
                for page in reader.pages[:3]:
                    text = page.extract_text()
                    if text:
                        content.append(text)
                return "\n".join(content)
        except Exception as e:
            console.print(f"[red]Error extracting PDF content: {str(e)}[/red]")
            return ""
            
    async def _load_and_process_document(self, file_path: Path) -> List[Document]:
        """Load and process a document into chunks."""
        try:
            self.current_file = file_path.name
            task = self.progress.add_task(f"Processing {file_path.name}", total=100)
            
            if file_path.suffix == '.pdf':
                self.progress.update(task, description=f"Loading PDF: {file_path.name}")
                content = await self._extract_pdf_content(file_path)
                self.progress.update(task, advance=30)
                if not content:
                    self.progress.update(task, completed=True)
                    return []
            else:
                self.progress.update(task, description=f"Loading text: {file_path.name}")
                loader = TextLoader(str(file_path))
                documents = loader.load()
                content = documents[0].page_content
                self.progress.update(task, advance=30)
            
            self.progress.update(task, description=f"Classifying: {file_path.name}")
            self.progress.update(task, advance=30)
            
            # Limit content to first 5000 characters
            sample_content = content[:5000]
            
            # Create a single document with the sample content
            sample_doc = Document(
                page_content=sample_content,
                metadata={
                    "source": str(file_path),
                    "filename": file_path.name,
                    "file_type": file_path.suffix,
                    "file_size": file_path.stat().st_size
                }
            )
            
            self.progress.update(task, completed=True)
            return [sample_doc]
            
        except Exception as e:
            self.progress.update(task, completed=True)
            console.print(f"[red]Error processing {file_path.name}: {str(e)}[/red]")
            return []
            
    async def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file and return its classification."""
        try:
            # Load and process document
            documents = await self._load_and_process_document(file_path)
            if not documents:
                return {
                    "file_path": str(file_path),
                    "error": "Failed to process document",
                    "success": False
                }
            
            # Classify the document
            classification = await self.classifier.classify_document(documents[0])
            
            return {
                "file_path": str(file_path),
                "classification": classification,
                "success": True
            }
            
        except Exception as e:
            return {
                "file_path": str(file_path),
                "error": str(e),
                "success": False
            }
    
    async def process_directory(self) -> List[Dict[str, Any]]:
        """Process all files in the directory."""
        results = []
        
        # Get all files
        files = []
        for ext in ['.pdf', '.txt', '.md']:
            found_files = list(self.directory.rglob(f'*{ext}'))
            files.extend(found_files)
            console.print(f"[cyan]Found {len(found_files)} {ext} files[/cyan]")
        
        if not files:
            console.print("[yellow]No supported files found in the directory[/yellow]")
            return results
        
        console.print(f"\n[cyan]Processing {len(files)} files...[/cyan]")
        
        # Process files with progress bar
        with self.progress:
            # Process files concurrently
            tasks = [self.process_file(file) for file in files]
            results = await asyncio.gather(*tasks)
        
        # Create summary table
        table = Table(title="Processing Summary")
        table.add_column("File", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Type", style="yellow")
        
        for result in results:
            if result["success"]:
                classification = result["classification"]
                table.add_row(
                    Path(result["file_path"]).name,
                    "✓",
                    classification["doc_type"]
                )
            else:
                table.add_row(
                    Path(result["file_path"]).name,
                    "✗",
                    result.get("error", "Unknown error")
                )
        
        console.print(table)
        return results

    def _generate_filename(self, classification: Dict[str, Any], original_path: Path) -> str:
        """Generate a new filename based on classification results."""
        metadata = classification["metadata"]
        doc_type = classification["doc_type"]
        
        if doc_type in [DocumentType.COMMERCIAL_DOCUMENT, DocumentType.LEGAL_DOCUMENT, 
                       DocumentType.NON_DISCLOSURE_AGREEMENT, DocumentType.PERSONAL_DOCUMENT]:
            # Commercial document format: date.company.name.doc_type.ext
            year = metadata.get('year', 'unknown')
            month = metadata.get('month', 'jan')
            day = metadata.get('day', '01')
            date = f"{year}_{month}_{day}"
            parts = [
                date,
                metadata.get("company", "unknown"),
                metadata.get("title", "unknown")[:50],
                doc_type
            ]
        else:
            # Academic document format: author.year.title.topic.doc_type.ext
            parts = [
                metadata.get("author", "unknown"),
                str(metadata.get("year", "unknown")),
                metadata.get("title", "unknown")[:50],
                metadata.get("topic", "MLAI"),  # Default to MLAI if no topic is found
                doc_type
            ]
        
        # Clean and join parts
        clean_parts = [self._clean_filename_part(part) for part in parts]
        base_name = ".".join(clean_parts)
        
        # Keep original extension
        return f"{base_name}{original_path.suffix}"
    
    def _clean_filename_part(self, part: str) -> str:
        """Clean a filename part to be filesystem-safe."""
        # Replace invalid characters and whitespace with underscore
        cleaned = "".join(c if c.isalnum() else "_" for c in str(part))
        # Remove duplicate underscores
        cleaned = "_".join(filter(None, cleaned.split("_")))
        return cleaned[:50]  # Limit length