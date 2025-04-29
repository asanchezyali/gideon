from enum import Enum
from typing import Dict, Any

from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.documents import Document

class DocumentMetadata(BaseModel):
    author: str | None = Field(description="Document author name")
    year: int | None = Field(description="Year the document was created")
    title: str | None = Field(description="Document title")
    topic: str | None = Field(description="Document topic or subject area")
    company: str | None = Field(description="Company name for commercial documents")
    month: str | None = Field(description="Month of document creation (3-letter code)")
    day: str | None = Field(description="Day of document creation (2-digit)")

class DocumentClassification(BaseModel):
    doc_type: str = Field(description="Type of document (Art|Book|Theses|CommDoc|LegalDoc|NDA|PersonalDoc)")
    metadata: DocumentMetadata = Field(description="Document metadata")
    confidence: float = Field(description="Classification confidence score between 0 and 1")
    reasoning: str = Field(description="Explanation for the classification decision")

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
        self.llm = Ollama(model="deepseek-coder:1.3b")
        self.parser = JsonOutputParser(pydantic_object=DocumentClassification)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert document classifier. Analyze the content and classify documents into appropriate categories."""),
            ("human", """Document types:
            - Art: Academic or research articles
            - Book: Books, ebooks, or long-form publications
            - Theses: Academic theses or dissertations
            - CommDoc: Commercial documents (contracts, proposals, reports)
            - LegalDoc: Legal documents (agreements, terms, policies)
            - NDA: Non-disclosure agreements
            - PersonalDoc: Personal documents (IDs, certificates, records)
            
            Classify the following document content and format your response as specified in the instructions:
            
            {content}
            
            {format_instructions}""")
        ])
        
        # Create LCEL chain
        self.chain = (
            self.prompt
            | self.llm
            | self.parser
        )
    
    async def classify_document(self, document: Document) -> Dict[str, Any]:
        """Classify a document and extract its metadata using the LLM."""
        try:
            result = await self.chain.ainvoke({
                "content": document.page_content,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            return {
                "doc_type": DocumentType(result.doc_type),
                "metadata": result.metadata.dict(),
                "confidence": float(result.confidence),
                "reasoning": result.reasoning
            }
        except Exception as e:
            return {
                "doc_type": DocumentType.COMMERCIAL_DOCUMENT,
                "metadata": {},
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}"
            }
    
    def validate_classification(self, classification: Dict[str, Any]) -> bool:
        """Validate the classification results."""
        try:
            # Convert to Pydantic model for validation
            doc_class = DocumentClassification(
                doc_type=classification["doc_type"],
                metadata=DocumentMetadata(**classification["metadata"]),
                confidence=classification["confidence"],
                reasoning=classification["reasoning"]
            )
            return doc_class.confidence > 0.7
        except Exception:
            return False