from enum import Enum
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel

from .base import BaseLLMService
from .ollama import OllamaService
from .dockerai import AiDockerModelService
from .openai_service import OpenAIService
from .anthropic_service import AnthropicService


class LLMServiceType(str, Enum):
    """Supported LLM service providers."""
    OLLAMA = "ollama"
    AI_DOCKER_MODEL = "docker-model"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class OllamaConfig(BaseModel):
    """Configuration for Ollama local LLM."""
    model: str
    temperature: float = 0.1


class AiDockerModelConfig(BaseModel):
    """Configuration for Docker AI Model."""
    model: str
    temperature: float = 0.1


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI GPT models."""
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.1
    api_key: Optional[str] = None
    max_tokens: Optional[int] = None
    timeout: int = 60


class AnthropicConfig(BaseModel):
    """Configuration for Anthropic Claude models."""
    model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.1
    api_key: Optional[str] = None
    max_tokens: int = 4096
    timeout: int = 60


class LLMServiceFactory:
    """Factory for creating LLM service instances."""

    _service_map: Dict[LLMServiceType, Type[BaseLLMService]] = {
        LLMServiceType.OLLAMA: OllamaService,
        LLMServiceType.AI_DOCKER_MODEL: AiDockerModelService,
        LLMServiceType.OPENAI: OpenAIService,
        LLMServiceType.ANTHROPIC: AnthropicService,
    }

    _config_map = {
        LLMServiceType.OLLAMA: OllamaConfig,
        LLMServiceType.AI_DOCKER_MODEL: AiDockerModelConfig,
        LLMServiceType.OPENAI: OpenAIConfig,
        LLMServiceType.ANTHROPIC: AnthropicConfig,
    }

    @classmethod
    def create(
        cls, service_type: LLMServiceType = LLMServiceType.OLLAMA, config: Optional[Dict[str, Any]] = None
    ) -> BaseLLMService:
        if service_type not in cls._service_map:
            supported = ", ".join(t.value for t in LLMServiceType)
            raise ValueError(f"Unsupported LLM type: {service_type}. Supported types are: {supported}")

        # Get the appropriate config model and service class
        config_model = cls._config_map[service_type]
        service_class = cls._service_map[service_type]

        # Validate configuration
        validated_config = config_model(**(config or {}))

        # Create service instance with validated config
        return service_class(config=validated_config.model_dump())

    @classmethod
    def get_default_config(cls, service_type: LLMServiceType) -> Dict[str, Any]:
        if service_type not in cls._config_map:
            supported = ", ".join(t.value for t in LLMServiceType)
            raise ValueError(f"Unsupported LLM type: {service_type}. Supported types are: {supported}")
        return cls._config_map[service_type]().model_dump()
