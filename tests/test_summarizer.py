"""Tests for document summarization service."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from src.gideon.services.summarizer import DocumentSummarizer, SummaryType


class TestDocumentSummarizer:
    """Test document summarizer functionality."""

    @pytest.fixture
    def summarizer(self):
        """Create a summarizer instance."""
        with patch('src.gideon.services.summarizer.LLMServiceFactory.create') as mock_factory:
            mock_llm = Mock()
            mock_llm.ainvoke = AsyncMock(return_value="Test summary of the document.")
            mock_factory.return_value = mock_llm
            return DocumentSummarizer()

    @pytest.mark.asyncio
    async def test_summarize_brief(self, summarizer, tmp_path):
        """Test brief summarization."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("This is test content for summarization.")

        with patch('src.gideon.services.summarizer.ExtractorFactory.get_extractor') as mock_extractor_factory:
            mock_extractor = Mock()
            mock_extractor.extract_content = AsyncMock(return_value="Test content")
            mock_extractor_factory.return_value = mock_extractor

            result = await summarizer.summarize_file(test_file, SummaryType.BRIEF)

            assert result['file'] == str(test_file)
            assert result['summary_type'] == 'brief'
            assert 'summary' in result
            assert result['truncated'] == False

    @pytest.mark.asyncio
    async def test_summarize_nonexistent_file(self, summarizer):
        """Test summarizing non-existent file."""
        with pytest.raises(FileNotFoundError):
            await summarizer.summarize_file(Path("/nonexistent/file.txt"))

    @pytest.mark.asyncio
    async def test_summarize_batch(self, summarizer, tmp_path):
        """Test batch summarization."""
        # Create test files
        files = []
        for i in range(3):
            test_file = tmp_path / f"test{i}.txt"
            test_file.write_text(f"Content {i}")
            files.append(test_file)

        with patch('src.gideon.services.summarizer.ExtractorFactory.get_extractor') as mock_extractor_factory:
            mock_extractor = Mock()
            mock_extractor.extract_content = AsyncMock(return_value="Test content")
            mock_extractor_factory.return_value = mock_extractor

            results = await summarizer.summarize_batch(files, SummaryType.BRIEF)

            assert len(results) == 3
            for result in results:
                assert 'summary_type' in result

    def test_summary_types_enum(self):
        """Test summary types enum."""
        assert SummaryType.BRIEF.value == "brief"
        assert SummaryType.STRUCTURED.value == "structured"
        assert SummaryType.DETAILED.value == "detailed"
        assert SummaryType.CORNELL.value == "cornell"
        assert SummaryType.TWEET.value == "tweet"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
