"""Base extractor for document content extraction."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ExtractedDocument:
    """Extracted document content and metadata."""
    content: str
    metadata: Dict[str, Any]
    format: str
    extraction_quality: float  # 0.0 - 1.0

    def __post_init__(self):
        """Validate extracted document."""
        if not 0.0 <= self.extraction_quality <= 1.0:
            raise ValueError("extraction_quality must be between 0.0 and 1.0")


class BaseExtractor(ABC):
    """Base class for document extractors."""

    @abstractmethod
    async def extract_content(self, file_path: Path) -> str:
        """
        Extract text content from document.

        Args:
            file_path: Path to document

        Returns:
            Extracted text content
        """
        pass

    @abstractmethod
    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from document.

        Args:
            file_path: Path to document

        Returns:
            Dictionary of metadata
        """
        pass

    async def extract(self, file_path: Path) -> ExtractedDocument:
        """
        Extract both content and metadata.

        Args:
            file_path: Path to document

        Returns:
            ExtractedDocument with content and metadata
        """
        content = await self.extract_content(file_path)
        metadata = await self.extract_metadata(file_path)

        return ExtractedDocument(
            content=content,
            metadata=metadata,
            format=file_path.suffix,
            extraction_quality=self._estimate_quality(content, metadata)
        )

    def _estimate_quality(self, content: str, metadata: Dict) -> float:
        """Estimate extraction quality score."""
        score = 0.5  # Base score

        # Content quality
        if len(content) > 100:
            score += 0.2
        if len(content) > 1000:
            score += 0.1

        # Metadata quality
        if metadata.get("title"):
            score += 0.1
        if metadata.get("author"):
            score += 0.1

        return min(score, 1.0)
