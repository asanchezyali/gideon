"""Factory for creating document extractors."""

from pathlib import Path
from typing import List, Type

from .base import BaseExtractor
from .pdf_extractor import PDFExtractor
from .docx_extractor import DocxExtractor
from .pptx_extractor import PptxExtractor
from .epub_extractor import EpubExtractor
from .text_extractor import TextExtractor, MarkdownExtractor
from .image_extractor import ImageOCRExtractor


class ExtractorFactory:
    """Factory for creating appropriate extractors based on file type."""

    EXTRACTOR_MAP = {
        # PDF
        ".pdf": PDFExtractor,
        # Microsoft Office
        ".docx": DocxExtractor,
        ".pptx": PptxExtractor,
        # Ebooks
        ".epub": EpubExtractor,
        # Text formats
        ".txt": TextExtractor,
        ".md": MarkdownExtractor,
        ".markdown": MarkdownExtractor,
        # Images (OCR)
        ".jpg": ImageOCRExtractor,
        ".jpeg": ImageOCRExtractor,
        ".png": ImageOCRExtractor,
        ".tiff": ImageOCRExtractor,
        ".tif": ImageOCRExtractor,
        ".bmp": ImageOCRExtractor,
    }

    @classmethod
    def get_extractor(cls, file_path: Path) -> BaseExtractor:
        """
        Get appropriate extractor for file.

        Args:
            file_path: Path to file

        Returns:
            Extractor instance

        Raises:
            ValueError: If file format not supported
        """
        extension = file_path.suffix.lower()

        if extension not in cls.EXTRACTOR_MAP:
            supported = ", ".join(cls.EXTRACTOR_MAP.keys())
            raise ValueError(
                f"Unsupported file format: {extension}\n"
                f"Supported formats: {supported}"
            )

        extractor_class = cls.EXTRACTOR_MAP[extension]
        return extractor_class()

    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of supported file extensions."""
        return list(cls.EXTRACTOR_MAP.keys())

    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        """Check if file format is supported."""
        return file_path.suffix.lower() in cls.EXTRACTOR_MAP

    @classmethod
    def register_extractor(cls, extension: str, extractor_class: Type[BaseExtractor]):
        """
        Register a new extractor for a file extension.

        Args:
            extension: File extension (e.g., '.docx')
            extractor_class: Extractor class to use
        """
        cls.EXTRACTOR_MAP[extension.lower()] = extractor_class
