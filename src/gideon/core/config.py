from pathlib import Path
from typing import Dict, Any, List
from pydantic_settings import BaseSettings
from dotenv import find_dotenv


class GideonSettings(BaseSettings):
    
    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    
    # LLM configurations
    DEFAULT_LLM_SERVICE_TYPE: str = "ollama"
    DEFAULT_LLM_MODEL: str = "deepseek-r1:latest"
    DEFAULT_LLM_TEMPERATURE: float = 0.1
    
    # File processing
    MAX_CONTENT_LENGTH: int = 500000
    SUPPORTED_EXTENSIONS: List[str] = [".pdf"]
    
    @property
    def DEFAULT_LLM_CONFIG(self) -> Dict[str, Any]:
        return {
            "model": self.DEFAULT_LLM_MODEL,
            "temperature": self.DEFAULT_LLM_TEMPERATURE,
        }
    
    class Config:
        env_file = find_dotenv('.env', usecwd=True) or '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'


settings = GideonSettings() 