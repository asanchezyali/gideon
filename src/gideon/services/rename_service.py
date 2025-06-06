from typing import Optional, Dict, Any, List
from ..models.document import DocumentInfo
from ..formarters.formarters import (
    AuthorFormatter,
    TitleFormatter,
    YearFormatter,
    TimestampFormatter,
    TopicFormatter,  # Assuming TopicFormatter is defined similarly
    FormatterInterface,
)
from ..core.config import settings
from ..llm.factory import LLMServiceType
from ..agents.renamer import DocumentAnalyzer
from ..agents.classifier import ClassifierWizard


class FileNameGenerator:
    def __init__(self, formatters: Optional[List[FormatterInterface]] = None):
        self.formatters = formatters or [
            AuthorFormatter(),
            YearFormatter(),
            TitleFormatter(),
            TimestampFormatter(),
            TopicFormatter(),
        ]

    def generate_filename(self, doc_info: DocumentInfo) -> str:
        filename_parts = []

        for formatter in self.formatters:
            formatted_part = formatter.format(doc_info)
            if formatted_part:
                filename_parts.append(formatted_part)

        return ".".join(filename_parts) + ".pdf"

    @classmethod
    def from_doc_info(cls, doc_info: DocumentInfo):
        generator = cls()
        return generator.generate_filename(doc_info)


class RenameService:
    def __init__(
        self,
        document_analyzer: Optional[DocumentAnalyzer] = None,
        document_classifier: Optional[ClassifierWizard] = None,
        filename_generator: Optional[FileNameGenerator] = None,
        llm_service_type: LLMServiceType = settings.DEFAULT_LLM_SERVICE_TYPE,
        service_config: Optional[Dict[str, Any]] = None,
    ):
        if document_analyzer is None:
            document_analyzer = DocumentAnalyzer(llm_service_type, service_config)
        self.document_analyzer = document_analyzer

        if document_classifier is None:
            document_classifier = ClassifierWizard(llm_service_type, service_config)
        self.document_classifier = document_classifier

        if filename_generator is None:
            filename_generator = FileNameGenerator()
        self.filename_generator = filename_generator

    async def rename_file(self, content: str, file_name: str) -> str:
        doc_info = await self.document_analyzer.analyze(content, file_name)
        if not doc_info:
            return file_name

        if not doc_info.title:
            topic_info = await self.document_classifier.classify(doc_info.title)
            print(f"Classified topic: {topic_info}")
            doc_info = DocumentInfo(
                authors=doc_info.authors,
                year=doc_info.year,
                title=doc_info.title or "Unknown_Title",
                topic=topic_info.get("topic", "Unknown_Topic"),
            )
        new_name = self.filename_generator.generate_filename(doc_info)
        return new_name
