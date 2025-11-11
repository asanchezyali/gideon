"""Literature review generation service."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

from langchain_core.prompts import PromptTemplate

from ..llm.factory import LLMServiceFactory, LLMServiceType
from ..search.semantic_search import SemanticSearchEngine
from ..utils.logging import log_info, log_success


class LiteratureReviewGenerator:
    """Generate literature reviews from document collections."""

    REVIEW_PROMPT = PromptTemplate.from_template("""
    Generate a comprehensive literature review on the topic: {topic}

    Based on the following research papers:
    {papers_summary}

    Structure the review with these sections:
    1. Introduction - Overview of the topic
    2. Key Themes - Main research themes and approaches
    3. Findings - Important findings and contributions
    4. Gaps - Identified gaps in the literature
    5. Future Directions - Suggested areas for future research

    Generate a well-structured literature review:
    """)

    def __init__(self, llm_type: Optional[LLMServiceType] = None, model: Optional[str] = None):
        config = {"temperature": 0.4}
        if model:
            config["model"] = model
        self.llm_service = LLMServiceFactory.create(llm_type, config)

    async def generate_review(
        self,
        topic: str,
        search_engine: SemanticSearchEngine,
        max_papers: int = 20
    ) -> str:
        """Generate literature review for a topic."""
        log_info(f"Searching for papers on: {topic}")

        # Search for relevant papers
        results = await search_engine.search(topic, k=max_papers)

        # Summarize papers
        papers_summary = "\n\n".join([
            f"Paper {i+1}: {r.chunk_text[:500]}..."
            for i, r in enumerate(results)
        ])

        log_info("Generating literature review...")
        prompt = self.REVIEW_PROMPT.format(topic=topic, papers_summary=papers_summary)
        review = await self.llm_service.ainvoke(prompt)

        log_success("Literature review generated")
        return review
