"""Reference and citation extraction service."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re
import json

from langchain_core.prompts import PromptTemplate
from pybtex.database import BibliographyData, Entry

from ..llm.factory import LLMServiceFactory, LLMServiceType
from ..extractors.factory import ExtractorFactory
from ..utils.logging import log_info, log_success, log_error


@dataclass
class Reference:
    """Represents a bibliographic reference."""
    authors: List[str]
    title: str
    year: Optional[str] = None
    venue: Optional[str] = None  # Journal, conference, or publisher
    volume: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    raw_text: Optional[str] = None

    def to_bibtex(self, cite_key: str) -> str:
        """Convert to BibTeX format."""
        entry_type = "article"  # Default type
        fields = {}

        if self.authors:
            fields['author'] = ' and '.join(self.authors)
        if self.title:
            fields['title'] = self.title
        if self.year:
            fields['year'] = self.year
        if self.venue:
            fields['journal'] = self.venue
        if self.volume:
            fields['volume'] = self.volume
        if self.pages:
            fields['pages'] = self.pages
        if self.doi:
            fields['doi'] = self.doi
        if self.url:
            fields['url'] = self.url

        # Format BibTeX entry
        lines = [f"@{entry_type}{{{cite_key},"]
        for key, value in fields.items():
            lines.append(f"  {key} = {{{value}}},")
        lines.append("}")

        return "\n".join(lines)

    def to_apa(self) -> str:
        """Convert to APA format."""
        parts = []

        # Authors
        if self.authors:
            if len(self.authors) == 1:
                parts.append(f"{self.authors[0]}.")
            elif len(self.authors) == 2:
                parts.append(f"{self.authors[0]} & {self.authors[1]}.")
            else:
                parts.append(f"{self.authors[0]} et al.")

        # Year
        if self.year:
            parts.append(f"({self.year}).")

        # Title
        if self.title:
            parts.append(f"{self.title}.")

        # Venue
        if self.venue:
            parts.append(f"*{self.venue}*")
            if self.volume:
                parts.append(f", *{self.volume}*")
            if self.pages:
                parts.append(f", {self.pages}.")

        # DOI/URL
        if self.doi:
            parts.append(f"https://doi.org/{self.doi}")
        elif self.url:
            parts.append(self.url)

        return " ".join(parts)


class ReferenceExtractor:
    """Service for extracting references and citations from documents."""

    EXTRACTION_PROMPT = PromptTemplate.from_template("""
    Extract all bibliographic references from the following document content.
    Return ONLY a JSON array where each reference has these fields:
    - authors: list of author names
    - title: paper/book title
    - year: publication year
    - venue: journal, conference, or publisher name
    - volume: volume number (if applicable)
    - pages: page range (if applicable)
    - doi: DOI (if present)
    - url: URL (if present)

    Document content (focusing on references section):
    {content}

    Return JSON array only, no other text:
    """)

    def __init__(
        self,
        llm_type: Optional[LLMServiceType] = None,
        model: Optional[str] = None
    ):
        """
        Initialize reference extractor.

        Args:
            llm_type: Type of LLM service to use
            model: Specific model to use
        """
        config = {"temperature": 0.1}  # Low temperature for accurate extraction
        if model:
            config["model"] = model

        self.llm_service = LLMServiceFactory.create(llm_type, config)

    async def extract_from_file(
        self,
        file_path: Path,
        use_llm: bool = True
    ) -> List[Reference]:
        """
        Extract references from a document.

        Args:
            file_path: Path to document
            use_llm: Whether to use LLM for extraction (more accurate but slower)

        Returns:
            List of extracted references

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If extraction fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Extract content
            log_info(f"Extracting content from {file_path.name}...")
            extractor = ExtractorFactory.get_extractor(file_path)
            content = await extractor.extract_content(file_path)

            # Try to isolate references section
            references_section = self._extract_references_section(content)
            if not references_section:
                references_section = content  # Use full content if no section found

            # Extract references
            if use_llm:
                log_info("Extracting references using LLM...")
                references = await self._extract_with_llm(references_section)
            else:
                log_info("Extracting references using patterns...")
                references = self._extract_with_patterns(references_section)

            log_success(f"Found {len(references)} references in {file_path.name}")
            return references

        except Exception as e:
            log_error(f"Failed to extract references from {file_path}: {str(e)}")
            raise ValueError(f"Reference extraction failed: {str(e)}")

    def _extract_references_section(self, content: str) -> Optional[str]:
        """
        Try to extract the references/bibliography section.

        Args:
            content: Full document content

        Returns:
            References section content or None
        """
        # Common section headers
        patterns = [
            r'(?i)\n\s*references?\s*\n',
            r'(?i)\n\s*bibliography\s*\n',
            r'(?i)\n\s*works?\s+cited\s*\n',
            r'(?i)\n\s*literatura?\s*\n',
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                # Extract from this point to the end
                return content[match.start():]

        return None

    async def _extract_with_llm(self, content: str) -> List[Reference]:
        """
        Extract references using LLM.

        Args:
            content: Content to extract from

        Returns:
            List of references
        """
        # Limit content length
        max_length = 50000
        if len(content) > max_length:
            content = content[:max_length]

        # Generate extraction
        prompt = self.EXTRACTION_PROMPT.format(content=content)
        response = await self.llm_service.ainvoke(prompt)

        # Parse JSON response
        try:
            # Try to extract JSON array from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)

                references = []
                for item in data:
                    ref = Reference(
                        authors=item.get('authors', []),
                        title=item.get('title', ''),
                        year=item.get('year'),
                        venue=item.get('venue'),
                        volume=item.get('volume'),
                        pages=item.get('pages'),
                        doi=item.get('doi'),
                        url=item.get('url'),
                        raw_text=None
                    )
                    references.append(ref)

                return references
            else:
                return []

        except Exception as e:
            log_error(f"Failed to parse LLM response: {str(e)}")
            return []

    def _extract_with_patterns(self, content: str) -> List[Reference]:
        """
        Extract references using pattern matching.

        Args:
            content: Content to extract from

        Returns:
            List of references
        """
        references = []

        # Simple pattern for common reference formats
        # Format: Authors (Year). Title. Venue.
        pattern = r'([A-Z][a-z]+(?:,?\s+[A-Z]\.?)+(?:,?\s+(?:and|&)\s+[A-Z][a-z]+(?:,?\s+[A-Z]\.?)+)*)\s*\((\d{4})\)\.\s+([^.]+)\.\s+([^.]+)\.'

        matches = re.finditer(pattern, content)

        for match in matches:
            authors_str, year, title, venue = match.groups()

            # Parse authors
            authors = []
            for author in re.split(r',?\s+(?:and|&)\s+', authors_str):
                authors.append(author.strip())

            ref = Reference(
                authors=authors,
                title=title.strip(),
                year=year,
                venue=venue.strip(),
                raw_text=match.group(0)
            )
            references.append(ref)

        return references

    async def export_references(
        self,
        references: List[Reference],
        output_path: Path,
        format: str = "bibtex"
    ):
        """
        Export references to file.

        Args:
            references: List of references
            output_path: Path to output file
            format: Export format (bibtex, apa, json)
        """
        try:
            if format == "bibtex":
                with open(output_path, 'w', encoding='utf-8') as f:
                    for i, ref in enumerate(references, 1):
                        cite_key = f"ref{i}"
                        if ref.authors and ref.year:
                            cite_key = f"{ref.authors[0].split()[-1]}{ref.year}"
                        f.write(ref.to_bibtex(cite_key))
                        f.write("\n\n")

            elif format == "apa":
                with open(output_path, 'w', encoding='utf-8') as f:
                    for ref in references:
                        f.write(ref.to_apa())
                        f.write("\n\n")

            elif format == "json":
                data = []
                for ref in references:
                    data.append({
                        "authors": ref.authors,
                        "title": ref.title,
                        "year": ref.year,
                        "venue": ref.venue,
                        "volume": ref.volume,
                        "pages": ref.pages,
                        "doi": ref.doi,
                        "url": ref.url,
                    })
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            log_success(f"References exported to {output_path}")

        except Exception as e:
            log_error(f"Failed to export references: {str(e)}")
            raise ValueError(f"Export failed: {str(e)}")

    def validate_references(self, references: List[Reference]) -> Dict[str, Any]:
        """
        Validate references and report issues.

        Args:
            references: List of references to validate

        Returns:
            Dictionary with validation results
        """
        issues = []

        for i, ref in enumerate(references, 1):
            ref_issues = []

            if not ref.authors or len(ref.authors) == 0:
                ref_issues.append("Missing authors")
            if not ref.title:
                ref_issues.append("Missing title")
            if not ref.year:
                ref_issues.append("Missing year")
            if not ref.venue:
                ref_issues.append("Missing venue")

            if ref_issues:
                issues.append({
                    "reference": i,
                    "title": ref.title or "Unknown",
                    "issues": ref_issues
                })

        valid_count = len(references) - len(issues)

        return {
            "total": len(references),
            "valid": valid_count,
            "invalid": len(issues),
            "issues": issues
        }
