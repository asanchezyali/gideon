"""Tests for document extractors."""

import pytest
from pathlib import Path
from src.gideon.extractors.factory import ExtractorFactory
from src.gideon.extractors.pdf_extractor import PDFExtractor


class TestExtractorFactory:
    """Test extractor factory."""

    def test_get_pdf_extractor(self):
        """Test getting PDF extractor."""
        extractor = ExtractorFactory.get_extractor(Path("test.pdf"))
        assert isinstance(extractor, PDFExtractor)

    def test_unsupported_format(self):
        """Test error on unsupported format."""
        with pytest.raises(ValueError):
            ExtractorFactory.get_extractor(Path("test.xyz"))

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        extensions = ExtractorFactory.get_supported_extensions()
        assert ".pdf" in extensions

    def test_is_supported(self):
        """Test checking if format is supported."""
        assert ExtractorFactory.is_supported(Path("test.pdf"))
        assert not ExtractorFactory.is_supported(Path("test.xyz"))


class TestPDFExtractor:
    """Test PDF extractor."""

    @pytest.mark.asyncio
    async def test_extract_content_nonexistent_file(self):
        """Test extracting content from nonexistent file."""
        extractor = PDFExtractor()
        content = await extractor.extract_content(Path("nonexistent.pdf"))
        assert content == ""

    @pytest.mark.asyncio
    async def test_extract_metadata_nonexistent_file(self):
        """Test extracting metadata from nonexistent file."""
        extractor = PDFExtractor()
        metadata = await extractor.extract_metadata(Path("nonexistent.pdf"))
        assert isinstance(metadata, dict)
        assert metadata.get("pages") == 0
