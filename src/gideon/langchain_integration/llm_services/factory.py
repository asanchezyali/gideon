"""Factory for creating LLM services."""
import os
from enum import Enum
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, Field

from .base import LLMServiceInterface
from .ollama_service import OllamaService
from .gemini_service import GeminiService

class LLMServiceType(str, Enum):
    """Supported LLM service types."""
    OLLAMA = "ollama"
    GEMINI = "gemini"

class OllamaConfig(BaseModel):
    """Configuration for Ollama service."""
    model_name: str = Field(default="deepseek-r1:latest")
    temperature: float = Field(default=0, ge=0, le=1)
    num_ctx: int = Field(default=4096, gt=0)
    repeat_penalty: float = Field(default=1.1, ge=1.0)
    seed: Optional[int] = Field(default=None)

class GeminiConfig(BaseModel):
    """Configuration for Gemini service."""
    model_name: str = Field(default="gemini-pro")
    temperature: float = Field(default=0, ge=0, le=1)
    top_p: float = Field(default=0.95, ge=0, le=1)
    top_k: int = Field(default=40, gt=0)
    max_output_tokens: int = Field(default=2048, gt=0)
    api_key: Optional[str] = Field(default=None)

class LLMServiceFactory:    
    _service_map: Dict[LLMServiceType, Type[LLMServiceInterface]] = {
        LLMServiceType.OLLAMA: OllamaService,
        LLMServiceType.GEMINI: GeminiService,
    }
    
    _config_map = {
        LLMServiceType.OLLAMA: OllamaConfig,
        LLMServiceType.GEMINI: GeminiConfig,
    }
    
    @classmethod
    def create(cls, 
              service_type: LLMServiceType, 
              config: Optional[Dict[str, Any]] = None, 
              **kwargs) -> LLMServiceInterface:

        if service_type not in cls._service_map:
            supported = ", ".join(t.value for t in LLMServiceType)
            raise ValueError(
                f"Unsupported LLM service type: {service_type}. "
                f"Supported types are: {supported}"
            )
        
        # Get the appropriate config model and service class
        config_model = cls._config_map[service_type]
        service_class = cls._service_map[service_type]
        
        # Combine config dict with kwargs
        combined_config = {**(config or {}), **kwargs}
        
        # Special handling for environment variables
        if service_type == LLMServiceType.GEMINI:
            api_key = combined_config.get('api_key') or os.getenv('GOOGLE_API_KEY')
            if api_key:
                combined_config['api_key'] = api_key
        
        # Validate and process configuration
        validated_config = config_model(**combined_config)
        
        # Create service instance with validated config
        return service_class(**validated_config.model_dump())
    
    @classmethod
    def get_default_config(cls, service_type: LLMServiceType) -> Dict[str, Any]:
        """Get the default configuration for a service type.
        
        Args:
            service_type: The service type to get defaults for
            
        Returns:
            Dictionary containing the default configuration
            
        Raises:
            ValueError: If the service type is not supported
        """
        if service_type not in cls._config_map:
            supported = ", ".join(t.value for t in LLMServiceType)
            raise ValueError(
                f"Unsupported LLM service type: {service_type}. "
                f"Supported types are: {supported}"
            )
            
        return cls._config_map[service_type]().model_dump()
    
    @classmethod
    def from_cli_args(cls, args: Any) -> LLMServiceInterface:
        """Create a service instance from CLI arguments.
        
        Args:
            args: Parsed command-line arguments containing service configuration
            
        Returns:
            Configured LLM service instance
        """
        service_type = LLMServiceType(args.llm_service)
        
        config = {}
        if hasattr(args, 'model_name'):
            config['model_name'] = args.model_name
            
        if hasattr(args, 'temperature'):
            config['temperature'] = args.temperature
            
        # Gemini-specific config
        if service_type == LLMServiceType.GEMINI:
            if hasattr(args, 'api_key'):
                config['api_key'] = args.api_key
            if hasattr(args, 'top_p'):
                config['top_p'] = args.top_p
            if hasattr(args, 'top_k'):
                config['top_k'] = args.top_k
            if hasattr(args, 'max_output_tokens'):
                config['max_output_tokens'] = args.max_output_tokens
                
        # Ollama-specific config
        elif service_type == LLMServiceType.OLLAMA:
            if hasattr(args, 'num_ctx'):
                config['num_ctx'] = args.num_ctx
            if hasattr(args, 'repeat_penalty'):
                config['repeat_penalty'] = args.repeat_penalty
            if hasattr(args, 'seed'):
                config['seed'] = args.seed
                
        return cls.create(service_type, config)