from pathlib import Path
from typing import List, Dict, Any, AsyncIterator
import asyncio
from enum import Enum
import json

from langchain_community.llms import Ollama
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.output_parsers import StrOutputParser

from .document_processor import DocumentProcessor
from .classifiers import DocumentClassifier, DocumentType

class ProcessingEvent(str, Enum):
    START = "start"
    LOAD = "load"
    CLASSIFY = "classify"
    MOVE = "move"
    COMPLETE = "complete"
    ERROR = "error"

class DocumentAgent:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.processor = DocumentProcessor()
        self.classifier = DocumentClassifier()
        self.llm = Ollama(model="deepseek-coder:1.3b")
        
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
        
        target_dir = self.base_path / type_to_dir[doc_type]
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
        
    async def process_file(self, file_path: str) -> AsyncIterator[Dict[str, Any]]:
        """Process a single file through the document pipeline with event streaming."""
        try:
            # Emit start event
            yield await self._emit_event(ProcessingEvent.START, file_path)
            
            # Check for duplicates first
            if self.processor.is_duplicate(file_path):
                yield await self._emit_event(
                    ProcessingEvent.ERROR,
                    file_path,
                    {"error": "Duplicate file detected", "is_duplicate": True}
                )
                return
            
            # Load and split document
            try:
                documents = self.processor.load_document(file_path)
                yield await self._emit_event(
                    ProcessingEvent.LOAD,
                    file_path,
                    {"chunks": len(documents)}
                )
            except Exception as e:
                yield await self._emit_event(
                    ProcessingEvent.ERROR,
                    file_path,
                    {"error": f"Failed to load document: {str(e)}"}
                )
                return
            
            # Get the most representative chunk for classification
            main_doc = max(documents, key=lambda x: len(x.page_content))
            
            # Classify document and extract metadata
            try:
                classification = await self.classifier.classify_document(main_doc)
                yield await self._emit_event(
                    ProcessingEvent.CLASSIFY,
                    file_path,
                    {
                        "classification": classification,
                        "confidence": classification["confidence"]
                    }
                )
            except Exception as e:
                yield await self._emit_event(
                    ProcessingEvent.ERROR,
                    file_path,
                    {"error": f"Failed to classify document: {str(e)}"}
                )
                return
            
            if not self.classifier.validate_classification(classification):
                yield await self._emit_event(
                    ProcessingEvent.ERROR,
                    file_path,
                    {"error": "Failed to validate document classification"}
                )
                return
            
            # Generate new filename and get target directory
            try:
                new_filename = self._generate_filename(classification, Path(file_path))
                target_dir = self._get_target_directory(classification["doc_type"])
                target_path = target_dir / new_filename
                
                # Move file to target directory
                target_path.parent.mkdir(parents=True, exist_ok=True)
                Path(file_path).rename(target_path)
                
                yield await self._emit_event(
                    ProcessingEvent.MOVE,
                    file_path,
                    {
                        "new_path": str(target_path),
                        "target_dir": str(target_dir)
                    }
                )
            except Exception as e:
                yield await self._emit_event(
                    ProcessingEvent.ERROR,
                    file_path,
                    {"error": f"Failed to move document: {str(e)}"}
                )
                return
            
            # Emit completion event with full results
            yield await self._emit_event(
                ProcessingEvent.COMPLETE,
                file_path,
                {
                    "original_path": file_path,
                    "new_path": str(target_path),
                    "classification": classification,
                    "metadata": self.processor.extract_metadata(main_doc)
                }
            )
            
        except Exception as e:
            yield await self._emit_event(
                ProcessingEvent.ERROR,
                file_path,
                {"error": str(e)}
            )
    
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
    
    async def process_directory(self, directory: str = None) -> AsyncIterator[Dict[str, Any]]:
        """Process all documents in a directory with event streaming."""
        if directory is None:
            directory = self.base_path
        
        path = Path(directory)
        
        # Process all files in directory
        tasks = []
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in [".pdf", ".txt", ".md", ".rst"]:
                # Create task for each file but don't await yet
                tasks.append(self.process_file(str(file_path)))
        
        if tasks:
            # Process files concurrently and stream events
            async def process_events():
                async for events in asyncio.as_completed([task for task in tasks]):
                    async for event in events:
                        yield event
            
            async for event in process_events():
                yield event