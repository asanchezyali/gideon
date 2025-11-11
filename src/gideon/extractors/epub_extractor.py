"""EPUB extractor."""

from pathlib import Path
from typing import Dict, Any
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from .base import BaseExtractor


class EpubExtractor(BaseExtractor):
    """Extractor for EPUB ebooks."""

    async def extract_content(self, file_path: Path) -> str:
        """
        Extract text content from EPUB file.

        Args:
            file_path: Path to .epub file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be read
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            book = epub.read_epub(str(file_path))
            chapters_text = []

            # Extract text from all document items
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # Parse HTML content
                    soup = BeautifulSoup(item.get_content(), 'html.parser')

                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    # Get text
                    text = soup.get_text()

                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)

                    if text.strip():
                        chapters_text.append(text)

            content = "\n\n".join(chapters_text)

            if not content.strip():
                return "Empty EPUB"

            return content

        except Exception as e:
            raise ValueError(f"Failed to extract content from {file_path}: {str(e)}")

    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from EPUB file.

        Args:
            file_path: Path to .epub file

        Returns:
            Dictionary containing metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If metadata cannot be extracted
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            book = epub.read_epub(str(file_path))

            # Helper to get metadata value
            def get_metadata(key):
                try:
                    values = book.get_metadata('DC', key)
                    return values[0][0] if values else ""
                except:
                    return ""

            metadata = {
                "title": get_metadata('title'),
                "author": get_metadata('creator'),
                "publisher": get_metadata('publisher'),
                "language": get_metadata('language'),
                "date": get_metadata('date'),
                "identifier": get_metadata('identifier'),
                "description": get_metadata('description'),
                "subject": get_metadata('subject'),
                "num_items": len(list(book.get_items())),
                "file_format": "epub",
            }

            return metadata

        except Exception as e:
            raise ValueError(f"Failed to extract metadata from {file_path}: {str(e)}")
