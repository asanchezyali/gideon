from enum import Enum
from typing import Dict, Any, List, Optional

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field
from langchain_core.documents import Document

from ..constants import DocType, TOPICS

class DocumentMetadata(BaseModel):
    author: str | None = Field(description="Document author name")
    year: int | None = Field(description="Year the document was created")
    title: str | None = Field(description="Document title")
    topic: str | None = Field(description="Document topic or subject area")
    company: str | None = Field(description="Company name for commercial documents")
    month: str | None = Field(description="Month of document creation (3-letter code)")
    day: str | None = Field(description="Day of document creation (2-digit)")

class DocumentClassification:
    def __init__(self, model_name: str = "llama3.1"):
        """Initialize the document classifier with a specific model."""
        self.model = ChatOllama(
            model=model_name,
            temperature=0,
            format="json"
        )
        
        self.prompt = ChatPromptTemplate.from_template(
            """You are a document classification expert. Your task is to analyze the content of a document and determine its type.
            
            Document Content:
            {content}
            
            Based on the content, classify this document into one of the following categories:
            - {categories}
            
            Return a JSON object with the following structure:
            {{
                "type": "the most appropriate category",
                "confidence": "a number between 0 and 1 indicating your confidence in the classification",
                "reasoning": "a brief explanation of why you chose this category"
            }}
            
            JSON Response:"""
        )
        
        self.chain = (
            {"content": RunnablePassthrough(), "categories": lambda _: ", ".join(DocType.list())}
            | self.prompt
            | self.model
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

class DocumentAgent:
    def __init__(self, model_name: str = "llama3.1"):
        """Initialize the document agent with a specific model."""
        self.classifier = DocumentClassification(model_name)
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a single document and return classification results."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            classification = await self.classifier.classify(content)
            return {
                "file_path": file_path,
                "classification": classification
            }
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return {
                "file_path": file_path,
                "error": str(e)
            }
    
    async def process_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Process all documents in a directory and return results."""
        from pathlib import Path
        from .utils import DirWalker
        
        results = []
        walker = DirWalker()
        
        for file_path in walker.walk(directory):
            if file_path.suffix.lower() in ['.txt', '.md', '.pdf']:
                result = await self.process_document(str(file_path))
                results.append(result)
        
        return results

class DocumentType(str, Enum):
    ARTICLE = "Art"
    BOOK = "Book"
    THESIS = "Theses"
    COMMERCIAL_DOCUMENT = "CommDoc"
    LEGAL_DOCUMENT = "LegalDoc"
    NON_DISCLOSURE_AGREEMENT = "NDA"
    PERSONAL_DOCUMENT = "PersonalDoc"

class DocumentClassifier:
    def __init__(self):
        self.model = ChatOllama(
            model="deepseek-coder:1.3b",
            temperature=0,
            format="json"
        )
        
        self.prompt = ChatPromptTemplate.from_template(
            """You are a document classification expert. Your task is to analyze the content of a document and determine its type.
            
            Document Content:
            {content}
            
            Based on the content, classify this document into one of the following categories:
            - {categories}
            
            Return a JSON object with the following structure:
            {{
                "type": "the most appropriate category",
                "confidence": "a number between 0 and 1 indicating your confidence in the classification",
                "reasoning": "a brief explanation of why you chose this category"
            }}
            
            JSON Response:"""
        )
        
        self.chain = (
            {"content": RunnablePassthrough(), "categories": lambda _: ", ".join(DocType.list())}
            | self.prompt
            | self.model
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