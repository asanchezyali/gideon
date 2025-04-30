import hashlib
from pathlib import Path
from typing import List, Set

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredFileLoader,
    UnstructuredPDFLoader
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

class DocumentProcessor:
    def __init__(self):
        # Initialize different text splitters for different document types
        self.default_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
            add_start_index=True
        )
        
        self.code_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,  # Default to Python, but we'll change based on file type
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )
        
        self.seen_hashes: Set[str] = set()
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load a document from file path and split it into chunks."""
        path = Path(file_path)
        
        # Calculate file hash before loading
        file_hash = self._calculate_file_hash(file_path)
        if file_hash in self.seen_hashes:
            raise ValueError(f"Duplicate file detected: {file_path}")
        self.seen_hashes.add(file_hash)
        
        # Choose appropriate loader and splitter based on file type
        if path.suffix.lower() == '.pdf':
            try:
                # Try UnstructuredPDFLoader first as it handles more complex PDFs
                loader = UnstructuredPDFLoader(file_path)
                documents = loader.load()
            except Exception:
                # Fall back to PyPDFLoader if UnstructuredPDFLoader fails
                loader = PyPDFLoader(file_path)
                documents = loader.load()
            splitter = self.default_splitter
            
        elif path.suffix.lower() in ['.py', '.js', '.java', '.cpp', '.cs']:
            loader = TextLoader(file_path)
            documents = loader.load()
            # Select appropriate language for code files
            lang_map = {
                '.py': Language.PYTHON,
                '.js': Language.JS,
                '.java': Language.JAVA,
                '.cpp': Language.CPP,
                '.cs': Language.CSHARP
            }
            self.code_splitter = RecursiveCharacterTextSplitter.from_language(
                language=lang_map.get(path.suffix.lower(), Language.PYTHON),
                chunk_size=1000,
                chunk_overlap=200,
                add_start_index=True
            )
            splitter = self.code_splitter
            
        elif path.suffix.lower() in ['.txt', '.md', '.rst']:
            loader = TextLoader(file_path)
            documents = loader.load()
            splitter = self.default_splitter
        else:
            # Use UnstructuredFileLoader for other file types
            loader = UnstructuredFileLoader(file_path)
            documents = loader.load()
            splitter = self.default_splitter
            
        # Add source file information to metadata
        for doc in documents:
            doc.metadata.update({
                "source": str(path),
                "file_type": path.suffix.lower(),
                "file_hash": file_hash
            })
            
        return splitter.split_documents(documents)
    
    def extract_metadata(self, document: Document) -> dict:
        """Extract relevant metadata from document content."""
        metadata = document.metadata.copy()
        
        # Add content statistics
        content_lines = document.page_content.split('\n')
        metadata.update({
            "source": str(Path(metadata.get("source", "")).name),
            "line_count": len(content_lines),
            "char_count": len(document.page_content),
            "word_count": len(document.page_content.split())
        })
        
        # Add position information if available
        if "start_index" in metadata:
            metadata["content_range"] = f"{metadata['start_index']}-{metadata['start_index'] + len(document.page_content)}"
        
        return metadata
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file."""
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
            
    def is_duplicate(self, file_path: str) -> bool:
        """Check if a file is a duplicate based on its hash."""
        file_hash = self._calculate_file_hash(file_path)
        return file_hash in self.seen_hashes