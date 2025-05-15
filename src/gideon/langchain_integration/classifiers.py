from enum import Enum
from typing import Dict, Any, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field
from langchain_core.documents import Document

from .llm_services import LLMServiceFactory, LLMServiceType
from ..constants import DocType

class DocumentMetadata(BaseModel):
    author: str | None = Field(description="Document author name")
    year: int | None = Field(description="Year the document was created")
    title: str | None = Field(description="Document title")
    topic: str | None = Field(description="Document topic or subject area")
    company: str | None = Field(description="Company name for commercial documents")
    month: str | None = Field(description="Month of document creation (3-letter code)")
    day: str | None = Field(description="Day of document creation (2-digit)")

class DocumentType(str, Enum):
    ARTICLE = "Art"
    BOOK = "Book"
    THESIS = "Theses"
    COMMERCIAL_DOCUMENT = "CommDoc"
    LEGAL_DOCUMENT = "LegalDoc"
    NON_DISCLOSURE_AGREEMENT = "NDA"
    PERSONAL_DOCUMENT = "PersonalDoc"

class DocumentClassifier:
    """Classifier for document types."""
    
    def __init__(self, service_type: LLMServiceType = LLMServiceType.OLLAMA,
                 service_config: Optional[Dict[str, Any]] = None):
        """Initialize the document classifier.
        
        Args:
            service_type: Type of LLM service to use
            service_config: Configuration for the LLM service
        """
        template = (
            "You are a document classification expert. Your task is to analyze "
            "the content of a document and determine its type."
        )
        
        self.llm_service = LLMServiceFactory.create(
            service_type,
            config=service_config or {"model_name": "deepseek-coder:1.3b"}
        )
        
        self.prompt = ChatPromptTemplate.from_template(
            f"""{template}
            
            Document Content:
            {{content}}
            
            Based on the content, classify this document into one of the following categories:
            - {{categories}}
            
            Return a JSON object with the following structure:
            {{{{
                "type": "the most appropriate category",
                "confidence": "a number between 0 and 1 indicating your confidence in the classification",
                "reasoning": "a brief explanation of why you chose this category"
            }}}}
            
            JSON Response:"""
        )
        
        self.chain = (
            {"content": RunnablePassthrough(), "categories": lambda _: ", ".join(DocType.list())}
            | self.prompt
            | self.llm_service.get_model()
            | JsonOutputParser()
        )
    
    async def classify(self, content: str) -> Dict[str, Any]:
        """Classify a document based on its content."""
        try:
            result = await self.chain.ainvoke(content)
            return result
        except Exception as e:
            print(f"Error in classification: {str(e)}")
            return {
                "type": DocType.UNKNOWN.value,
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}"
            }

    async def classify_document(self, document: Document) -> Dict[str, Any]:
        """Classify a document and extract its metadata using the LLM."""
        try:
            result = await self.chain.ainvoke(document.page_content)
            
            return {
                "type": DocType(result["type"]),
                "confidence": result["confidence"],
                "reasoning": result["reasoning"]
            }
        except Exception as e:
            return {
                "type": DocType.COMMERCIAL_DOCUMENT,
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}"
            }
    
    def validate_classification(self, classification: Dict[str, Any]) -> bool:
        """Validate the classification results."""
        try:
            return classification["confidence"] > 0.7
        except Exception:
            return False