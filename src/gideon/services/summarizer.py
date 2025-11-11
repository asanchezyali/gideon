"""Document summarization service."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
import json

from langchain_core.prompts import PromptTemplate

from ..llm.factory import LLMServiceFactory, LLMServiceType
from ..extractors.factory import ExtractorFactory
from ..utils.logging import log_info, log_success, log_error


class SummaryType(str, Enum):
    """Types of document summaries."""
    BRIEF = "brief"
    STRUCTURED = "structured"
    DETAILED = "detailed"
    CORNELL = "cornell"
    TWEET = "tweet"


class DocumentSummarizer:
    """Service for generating document summaries using LLMs."""

    BRIEF_PROMPT = PromptTemplate.from_template("""
    Summarize the following document in 2-3 concise sentences. Focus on the main point and key takeaways.

    Document content:
    {content}

    Brief summary (2-3 sentences):
    """)

    STRUCTURED_PROMPT = PromptTemplate.from_template("""
    Generate a structured summary of the following document in JSON format.

    Document content:
    {content}

    Provide the summary in this exact JSON format:
    {{
        "main_contribution": "One sentence describing the main contribution",
        "key_findings": ["finding 1", "finding 2", "finding 3"],
        "methodology": "Brief description of methodology used",
        "limitations": "Key limitations discussed",
        "future_work": "Suggestions for future research"
    }}

    Structured summary (JSON only, no other text):
    """)

    DETAILED_PROMPT = PromptTemplate.from_template("""
    Generate a comprehensive summary of the following document. Include:
    - Main topic and purpose
    - Key arguments and findings
    - Methodology (if applicable)
    - Important details and evidence
    - Conclusions and implications

    Document content:
    {content}

    Detailed summary:
    """)

    CORNELL_PROMPT = PromptTemplate.from_template("""
    Generate Cornell-style notes for the following document. Format:

    **Main Ideas:**
    - [Key concept 1]
    - [Key concept 2]

    **Details:**
    - Supporting details and examples

    **Questions:**
    - Important questions raised

    **Summary:**
    - Brief synthesis

    Document content:
    {content}

    Cornell notes:
    """)

    TWEET_PROMPT = PromptTemplate.from_template("""
    Summarize the following document in a single tweet (max 280 characters).
    Make it engaging and capture the essence.

    Document content:
    {content}

    Tweet (280 chars max):
    """)

    def __init__(
        self,
        llm_type: Optional[LLMServiceType] = None,
        model: Optional[str] = None,
        temperature: float = 0.3
    ):
        """
        Initialize document summarizer.

        Args:
            llm_type: Type of LLM service to use
            model: Specific model to use
            temperature: Temperature for generation (0.0-1.0)
        """
        config = {"temperature": temperature}
        if model:
            config["model"] = model

        self.llm_service = LLMServiceFactory.create(llm_type, config)

    async def summarize_file(
        self,
        file_path: Path,
        summary_type: SummaryType = SummaryType.BRIEF,
        max_content_length: int = 50000
    ) -> Dict[str, Any]:
        """
        Summarize a single document.

        Args:
            file_path: Path to document
            summary_type: Type of summary to generate
            max_content_length: Maximum content length to process

        Returns:
            Dictionary containing summary and metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If summarization fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Extract content
            log_info(f"Extracting content from {file_path.name}...")
            extractor = ExtractorFactory.get_extractor(file_path)
            content = await extractor.extract_content(file_path)

            # Truncate if too long
            if len(content) > max_content_length:
                log_info(f"Content truncated to {max_content_length} characters")
                content = content[:max_content_length] + "..."

            # Generate summary
            log_info(f"Generating {summary_type.value} summary...")
            summary = await self._generate_summary(content, summary_type)

            result = {
                "file": str(file_path),
                "summary_type": summary_type.value,
                "summary": summary,
                "content_length": len(content),
                "truncated": len(content) > max_content_length,
            }

            log_success(f"Summary generated for {file_path.name}")
            return result

        except Exception as e:
            log_error(f"Failed to summarize {file_path}: {str(e)}")
            raise ValueError(f"Summarization failed: {str(e)}")

    async def summarize_batch(
        self,
        file_paths: List[Path],
        summary_type: SummaryType = SummaryType.BRIEF,
        max_content_length: int = 50000
    ) -> List[Dict[str, Any]]:
        """
        Summarize multiple documents.

        Args:
            file_paths: List of file paths
            summary_type: Type of summary to generate
            max_content_length: Maximum content length to process

        Returns:
            List of summary results
        """
        results = []
        total = len(file_paths)

        for i, file_path in enumerate(file_paths, 1):
            log_info(f"Processing {i}/{total}: {file_path.name}")
            try:
                result = await self.summarize_file(file_path, summary_type, max_content_length)
                results.append(result)
            except Exception as e:
                log_error(f"Failed to process {file_path.name}: {str(e)}")
                results.append({
                    "file": str(file_path),
                    "error": str(e),
                    "summary_type": summary_type.value,
                })

        log_success(f"Processed {len(results)}/{total} files")
        return results

    async def _generate_summary(self, content: str, summary_type: SummaryType) -> str:
        """
        Generate summary using appropriate prompt.

        Args:
            content: Document content
            summary_type: Type of summary

        Returns:
            Generated summary
        """
        # Select prompt based on type
        prompt_map = {
            SummaryType.BRIEF: self.BRIEF_PROMPT,
            SummaryType.STRUCTURED: self.STRUCTURED_PROMPT,
            SummaryType.DETAILED: self.DETAILED_PROMPT,
            SummaryType.CORNELL: self.CORNELL_PROMPT,
            SummaryType.TWEET: self.TWEET_PROMPT,
        }

        prompt = prompt_map[summary_type]
        formatted_prompt = prompt.format(content=content)

        # Generate summary
        response = await self.llm_service.ainvoke(formatted_prompt)
        summary = response.strip()

        # Parse JSON for structured summaries
        if summary_type == SummaryType.STRUCTURED:
            try:
                # Try to extract JSON from response
                json_start = summary.find('{')
                json_end = summary.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    summary = summary[json_start:json_end]
                # Validate JSON
                json.loads(summary)
            except:
                # If JSON parsing fails, keep original response
                pass

        return summary

    async def export_summaries(
        self,
        summaries: List[Dict[str, Any]],
        output_path: Path,
        format: str = "markdown"
    ):
        """
        Export summaries to file.

        Args:
            summaries: List of summary results
            output_path: Path to output file
            format: Export format (markdown, json, txt)
        """
        try:
            if format == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(summaries, f, indent=2, ensure_ascii=False)

            elif format == "markdown":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("# Document Summaries\n\n")
                    for i, result in enumerate(summaries, 1):
                        f.write(f"## {i}. {Path(result['file']).name}\n\n")
                        if 'error' in result:
                            f.write(f"**Error:** {result['error']}\n\n")
                        else:
                            f.write(f"**Type:** {result['summary_type']}\n\n")
                            f.write(f"{result['summary']}\n\n")
                            f.write("---\n\n")

            elif format == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    for result in summaries:
                        f.write(f"File: {result['file']}\n")
                        if 'error' in result:
                            f.write(f"Error: {result['error']}\n")
                        else:
                            f.write(f"Type: {result['summary_type']}\n")
                            f.write(f"Summary:\n{result['summary']}\n")
                        f.write("\n" + "="*80 + "\n\n")

            log_success(f"Summaries exported to {output_path}")

        except Exception as e:
            log_error(f"Failed to export summaries: {str(e)}")
            raise ValueError(f"Export failed: {str(e)}")
