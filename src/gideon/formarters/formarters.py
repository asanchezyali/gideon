from typing import List, Protocol, Optional
import re
from datetime import datetime
from ..models.document import DocumentInfo, UNKNOWN_AUTHOR, UNKNOWN_TITLE, UNKNOWN_TOPIC, TOPIC_LIST


class FormatterInterface(Protocol):
    def format(self, doc_info: DocumentInfo) -> str:
        """Format a part of document info into a string for filename."""
        ...


class AuthorFormatter:
    def format(self, doc_info: DocumentInfo) -> str:
        return AuthorFormatter.format_authors(doc_info.authors)

    @staticmethod
    def format_authors(authors: List[str]) -> str:
        if not authors:
            return UNKNOWN_AUTHOR

        if len(authors) > 1:
            first_author = re.sub(r"[^\w\s]", "", authors[0])
            formatted_author = "_".join(word.capitalize() for word in first_author.split())
            return f"{formatted_author}_And_Others"
        else:
            clean_author = re.sub(r"[^\w\s]", "", authors[0])
            formatted_author = "_".join(word.capitalize() for word in clean_author.split())
            return formatted_author


class TitleFormatter:
    def format(self, doc_info: DocumentInfo) -> str:
        return TitleFormatter.format_title(doc_info.title)

    @staticmethod
    def format_title(title: str) -> str:
        if not title:
            return UNKNOWN_TITLE
        clean_title = re.sub(r"[^\w\s]", "", title)
        words = clean_title.lower().split()
        if words:
            words[0] = words[0].capitalize()
        formatted_title = "_".join(words)
        return formatted_title


class YearFormatter:
    def format(self, doc_info: DocumentInfo) -> str:
        return YearFormatter.format_year(doc_info.year)

    @staticmethod
    def format_year(year: str) -> str:
        return year[:4] if year else ""


class TimestampFormatter:
    def format(self, doc_info: DocumentInfo) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")


class TopicFormatter:
    def format(self, doc_info: DocumentInfo) -> str:
        return TopicFormatter.format_topic(doc_info.topic)

    @staticmethod
    def format_topic(topic: str) -> str:
        if not topic:
            return UNKNOWN_TOPIC
        words = re.split(r'[_\s]+', topic)
        formatted = "_".join(word.capitalize() for word in words if word)
        return formatted


class FileNameGenerator:
    def __init__(self, formatters: Optional[List[FormatterInterface]] = None):
        self.formatters = formatters or [AuthorFormatter(), YearFormatter(), TitleFormatter(), TimestampFormatter()]

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
