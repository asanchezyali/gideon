"""Tests for LLM factory."""

import pytest
from src.gideon.llm.factory import LLMServiceFactory, LLMServiceType
from src.gideon.llm.openai_service import OpenAIService
from src.gideon.llm.anthropic_service import AnthropicService
from src.gideon.llm.ollama import OllamaService


class TestLLMFactory:
    """Test LLM service factory."""

    def test_create_openai_service(self):
        """Test creating OpenAI service."""
        service = LLMServiceFactory.create(
            service_type=LLMServiceType.OPENAI,
            config={"model": "gpt-4", "api_key": "test-key"}
        )
        assert isinstance(service, OpenAIService)

    def test_create_anthropic_service(self):
        """Test creating Anthropic service."""
        service = LLMServiceFactory.create(
            service_type=LLMServiceType.ANTHROPIC,
            config={"model": "claude-3-sonnet", "api_key": "test-key"}
        )
        assert isinstance(service, AnthropicService)

    def test_create_ollama_service(self):
        """Test creating Ollama service."""
        service = LLMServiceFactory.create(
            service_type=LLMServiceType.OLLAMA,
            config={"model": "llama2"}
        )
        assert isinstance(service, OllamaService)

    def test_unsupported_service_type(self):
        """Test error on unsupported service type."""
        with pytest.raises(ValueError):
            LLMServiceFactory.create(service_type="unsupported")

    def test_get_supported_extensions(self):
        """Test getting supported LLM types."""
        types = list(LLMServiceType)
        assert LLMServiceType.OPENAI in types
        assert LLMServiceType.ANTHROPIC in types
        assert LLMServiceType.OLLAMA in types
