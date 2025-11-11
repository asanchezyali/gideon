"""PDF document extractor."""

from pathlib import Path
from typing import Dict, Any
from PyPDF2 import PdfReader

from .base import BaseExtractor
from ..core.config import settings
from ..utils.logging import log_error


class PDFExtractor(BaseExtractor):
    """Extract content from PDF files."""

    async def extract_content(self, file_path: Path) -> str:
        """Extract text from PDF."""
        try:
            reader = PdfReader(str(file_path))
            pages = reader.pages[:settings.MAX_PDF_PAGES]
            text = "\n".join([
                page.extract_text()
                for page in pages
                if page.extract_text()
            ])
            return text
        except Exception as e:
            log_error(f"Error extracting PDF content from {file_path}: {e}")
            return ""

    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract PDF metadata."""
        try:
            reader = PdfReader(str(file_path))
            metadata = reader.metadata or {}

            return {
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "subject": metadata.get("/Subject", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", ""),
                "creation_date": metadata.get("/CreationDate", ""),
                "pages": len(reader.pages),
                "file_size": file_path.stat().st_size,
            }
        except Exception as e:
            log_error(f"Error extracting PDF metadata from {file_path}: {e}")
            return {
                "pages": 0,
                "file_size": file_path.stat().st_size if file_path.exists() else 0,
            }
