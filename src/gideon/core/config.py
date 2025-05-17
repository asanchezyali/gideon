from pathlib import Path
from typing import Dict, Any
from pydantic_settings import BaseSettings


class GideonSettings(BaseSettings):
    """Global settings for Gideon."""
    
    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    
    # LLM configurations
    DEFAULT_LLM_TYPE: str = "ollama"
    DEFAULT_LLM_CONFIG: Dict[str, Any] = {
        "model": "deepseek-r1:latest",
        "temperature": 0.1,
    }
    
    # File processing
    MAX_CONTENT_LENGTH: int = 5000
    SUPPORTED_EXTENSIONS: list[str] = [".pdf"]


settings = GideonSettings() 