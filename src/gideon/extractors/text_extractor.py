"""Plain text and Markdown extractor."""

from pathlib import Path
from typing import Dict, Any
import markdown
from bs4 import BeautifulSoup

from .base import BaseExtractor


class TextExtractor(BaseExtractor):
    """Extractor for plain text files (.txt)."""

    async def extract_content(self, file_path: Path) -> str:
        """
        Extract text content from text file.

        Args:
            file_path: Path to .txt file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be read
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                return "Empty file"

            return content

        except Exception as e:
            raise ValueError(f"Failed to extract content from {file_path}: {str(e)}")

    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from text file.

        Args:
            file_path: Path to .txt file

        Returns:
            Dictionary containing metadata
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            content = await self.extract_content(file_path)
            lines = content.splitlines()
            words = content.split()

            metadata = {
                "title": file_path.stem,
                "num_lines": len(lines),
                "num_words": len(words),
                "num_characters": len(content),
                "file_format": "txt",
            }

            return metadata

        except Exception as e:
            raise ValueError(f"Failed to extract metadata from {file_path}: {str(e)}")


class MarkdownExtractor(BaseExtractor):
    """Extractor for Markdown files (.md)."""

    async def extract_content(self, file_path: Path) -> str:
        """
        Extract text content from Markdown file.

        Args:
            file_path: Path to .md file

        Returns:
            Extracted text content (converted from Markdown)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be read
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                md_content = f.read()

            # Convert Markdown to HTML, then extract text
            html = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            if not text.strip():
                return "Empty file"

            return text

        except Exception as e:
            raise ValueError(f"Failed to extract content from {file_path}: {str(e)}")

    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from Markdown file.

        Args:
            file_path: Path to .md file

        Returns:
            Dictionary containing metadata
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.splitlines()
            words = content.split()

            # Extract title from first heading if present
            title = file_path.stem
            for line in lines:
                if line.startswith('# '):
                    title = line.replace('# ', '').strip()
                    break

            metadata = {
                "title": title,
                "num_lines": len(lines),
                "num_words": len(words),
                "num_characters": len(content),
                "file_format": "markdown",
            }

            return metadata

        except Exception as e:
            raise ValueError(f"Failed to extract metadata from {file_path}: {str(e)}")
