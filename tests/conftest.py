"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    return """
    Attention Is All You Need

    Ashish Vaswani, Noam Shazeer, Niki Parmar

    2017

    Abstract: The dominant sequence transduction models are based on complex
    recurrent or convolutional neural networks...
    """


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("DEFAULT_LLM_SERVICE_TYPE", "ollama")
