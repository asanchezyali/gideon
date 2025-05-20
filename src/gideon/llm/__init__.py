from enum import Enum
from typing import Dict, Any, Optional

from .base import BaseLLMService
from .ollama import OllamaService


class LLMType(str, Enum):
    """Supported LLM types."""
    OLLAMA = "ollama"
    # Add more LLM types here as they are implemented


def create_llm_service(
    llm_type: LLMType = LLMType.OLLAMA,
    config: Optional[Dict[str, Any]] = None
) -> BaseLLMService:
    """Create a LLM service instance.
    
    Args:
        llm_type: Type of LLM service to create
        config: Configuration for the LLM service
        
    Returns:
        An instance of the requested LLM service
        
    Raises:
        ValueError: If the requested LLM type is not supported
    """
    if llm_type == LLMType.OLLAMA:
        return OllamaService(config)
    raise ValueError(f"Unsupported LLM type: {llm_type}") 