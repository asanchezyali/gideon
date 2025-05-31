from enum import Enum
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel

from .base import BaseLLMService
from .ollama import OllamaService
from .ai_docker_model import AiDockerModelService


class LLMServiceType(str, Enum):
    OLLAMA = "ollama"
    AI_DOCKER_MODEL = "docker-model"


class OllamaConfig(BaseModel):
    model: str
    temperature: float = 0.1


class AiDockerModelConfig(BaseModel):
    model: str
    temperature: float = 0.1


class LLMServiceFactory:
    _service_map: Dict[LLMServiceType, Type[BaseLLMService]] = {
        LLMServiceType.OLLAMA: OllamaService,
        LLMServiceType.AI_DOCKER_MODEL: AiDockerModelService,
    }

    _config_map = {
        LLMServiceType.OLLAMA: OllamaConfig,
        LLMServiceType.AI_DOCKER_MODEL: AiDockerModelConfig,
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
