from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GideonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent.parent / '.env'),
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
    
    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    
    # LLM configurations
    DEFAULT_LLM_SERVICE_TYPE: str = Field(default="ollama")
    DEFAULT_LLM_MODEL: str = Field(default="deepseek-r1:latest")
    DEFAULT_LLM_TEMPERATURE: float = Field(default=0.1)
    
    # File processing
    MAX_CONTENT_LENGTH: int = Field(default=500000)
    MAX_PDF_PAGES: int = Field(default=5)
    SUPPORTED_EXTENSIONS: List[str] = Field(default=[".pdf"])
    
    @property
    def DEFAULT_LLM_CONFIG(self) -> Dict[str, Any]:
        return {
            "model": self.DEFAULT_LLM_MODEL,
            "temperature": self.DEFAULT_LLM_TEMPERATURE,
        }


settings = GideonSettings() 