from enum import Enum
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel

from .base import BaseLLMService
from .ollama import OllamaService


class LLMServiceType(str, Enum):
    """Supported LLM service types."""
    OLLAMA = "ollama"
    # Add more LLM types here as they are implemented


class OllamaConfig(BaseModel):
    """Configuration for Ollama service."""
    model: str
    temperature: float = 0.1


class LLMServiceFactory:
    """Factory for creating LLM services."""
    
    _service_map: Dict[LLMServiceType, Type[BaseLLMService]] = {
        LLMServiceType.OLLAMA: OllamaService,
    }
    
    _config_map = {
        LLMServiceType.OLLAMA: OllamaConfig,
    }
    
    @classmethod
    def create(
        cls,
        service_type: LLMServiceType = LLMServiceType.OLLAMA,
        config: Optional[Dict[str, Any]] = None
    ) -> BaseLLMService:
        """Create a LLM service instance.
        
        Args:
            service_type: Type of LLM service to create
            config: Configuration for the LLM service
            
        Returns:
            An instance of the requested LLM service
            
        Raises:
            ValueError: If the requested LLM type is not supported
        """
        if service_type not in cls._service_map:
            supported = ", ".join(t.value for t in LLMServiceType)
            raise ValueError(
                f"Unsupported LLM type: {service_type}. "
                f"Supported types are: {supported}"
            )
        
        # Get the appropriate config model and service class
        config_model = cls._config_map[service_type]
        service_class = cls._service_map[service_type]
        
        # Validate configuration
        validated_config = config_model(**(config or {}))
        
        # Create service instance with validated config
        return service_class(config=validated_config.model_dump())
    
    @classmethod
    def get_default_config(cls, service_type: LLMServiceType) -> Dict[str, Any]:
        """Get the default configuration for a service type."""
        if service_type not in cls._config_map:
            supported = ", ".join(t.value for t in LLMServiceType)
            raise ValueError(
                f"Unsupported LLM type: {service_type}. "
                f"Supported types are: {supported}"
            )
        return cls._config_map[service_type]().model_dump() 