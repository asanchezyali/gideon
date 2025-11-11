"""CLI commands for literature review generation."""

from pathlib import Path
from typing import Optional
import asyncio

import typer
from rich.console import Console

from ...services.literature_review import LiteratureReviewGenerator
from ...search.semantic_search import SemanticSearchEngine
from ...llm.factory import LLMServiceType
from ...utils.logging import log_error

app = typer.Typer(help="Literature review generation")
console = Console()


@app.command("generate")
def generate_review(
    topic: str = typer.Argument(..., help="Research topic"),
    index_path: Path = typer.Option(".gideon/vectorstore", "--index", help="Path to search index"),
    max_papers: int = typer.Option(20, "--max-papers", help="Maximum papers to include"),
    llm_type: Optional[LLMServiceType] = typer.Option(None, "--llm", help="LLM service"),
    output: Path = typer.Option("review.md", "--output", "-o", help="Output file"),
):
    """
    Generate literature review for a topic.

    Example:
        gideon review generate "transformers in NLP" --output review.md
    """
    asyncio.run(_generate_review(topic, index_path, max_papers, llm_type, output))


async def _generate_review(
    topic: str,
    index_path: Path,
    max_papers: int,
    llm_type: Optional[LLMServiceType],
    output: Path
):
    """Async implementation."""
    try:
        console.print(f"\n[cyan]Generating literature review on: {topic}[/cyan]\n")

        # Initialize services
        search_engine = SemanticSearchEngine(persist_directory=index_path)
        generator = LiteratureReviewGenerator(llm_type=llm_type)

        # Generate review
        review = await generator.generate_review(topic, search_engine, max_papers)

        # Save to file
        with open(output, 'w', encoding='utf-8') as f:
            f.write(f"# Literature Review: {topic}\n\n")
            f.write(review)

        console.print(f"\n[green]✓ Literature review generated[/green]")
        console.print(f"[bold]Output:[/bold] {output}")

    except Exception as e:
        log_error(f"Failed to generate review: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
