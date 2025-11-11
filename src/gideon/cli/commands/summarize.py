"""CLI commands for document summarization."""

from pathlib import Path
from typing import Optional
import asyncio

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from ...services.summarizer import DocumentSummarizer, SummaryType
from ...llm.factory import LLMServiceType
from ...utils.logging import log_info, log_error

app = typer.Typer(help="Document summarization commands")
console = Console()


@app.command("file")
def summarize_file(
    file_path: Path = typer.Argument(..., help="Path to document to summarize"),
    summary_type: SummaryType = typer.Option(
        SummaryType.BRIEF,
        "--type",
        "-t",
        help="Type of summary (brief, structured, detailed, cornell, tweet)"
    ),
    llm_type: Optional[LLMServiceType] = typer.Option(
        None,
        "--llm",
        help="LLM service to use (openai, anthropic, ollama)"
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Specific model to use"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save summary to file"),
):
    """
    Summarize a single document.

    Example:
        gideon summarize file document.pdf --type structured
    """
    asyncio.run(_summarize_file(file_path, summary_type, llm_type, model, output))


async def _summarize_file(
    file_path: Path,
    summary_type: SummaryType,
    llm_type: Optional[LLMServiceType],
    model: Optional[str],
    output: Optional[Path]
):
    """Async implementation of file summarization."""
    if not file_path.exists():
        log_error(f"File not found: {file_path}")
        raise typer.Exit(1)

    try:
        # Create summarizer
        console.print(f"\n[cyan]Summarizing {file_path.name}...[/cyan]")
        summarizer = DocumentSummarizer(llm_type=llm_type, model=model)

        # Generate summary
        result = await summarizer.summarize_file(file_path, summary_type)

        # Display result
        console.print(f"\n[green]✓ Summary generated[/green]\n")
        console.print(f"[bold]File:[/bold] {file_path.name}")
        console.print(f"[bold]Type:[/bold] {summary_type.value}")
        console.print(f"[bold]Content length:[/bold] {result['content_length']} characters")
        if result['truncated']:
            console.print("[yellow]⚠ Content was truncated[/yellow]")

        console.print(f"\n[bold cyan]Summary:[/bold cyan]")
        console.print(result['summary'])

        # Save to file if requested
        if output:
            await summarizer.export_summaries([result], output, format="markdown")
            console.print(f"\n[green]✓ Summary saved to {output}[/green]")

    except Exception as e:
        log_error(f"Summarization failed: {str(e)}")
        raise typer.Exit(1)


@app.command("batch")
def summarize_batch(
    directory: Path = typer.Argument(..., help="Directory containing documents"),
    summary_type: SummaryType = typer.Option(
        SummaryType.BRIEF,
        "--type",
        "-t",
        help="Type of summary"
    ),
    pattern: str = typer.Option("**/*.*", "--pattern", "-p", help="File pattern to match"),
    llm_type: Optional[LLMServiceType] = typer.Option(None, "--llm", help="LLM service to use"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Specific model to use"),
    output: Path = typer.Option("summaries.md", "--output", "-o", help="Output file"),
    export_format: str = typer.Option("markdown", "--format", "-f", help="Export format (markdown, json, txt)"),
):
    """
    Summarize multiple documents in a directory.

    Example:
        gideon summarize batch ./documents/ --type brief --output summaries.md
    """
    asyncio.run(_summarize_batch(directory, summary_type, pattern, llm_type, model, output, export_format))


async def _summarize_batch(
    directory: Path,
    summary_type: SummaryType,
    pattern: str,
    llm_type: Optional[LLMServiceType],
    model: Optional[str],
    output: Path,
    export_format: str
):
    """Async implementation of batch summarization."""
    if not directory.exists():
        log_error(f"Directory not found: {directory}")
        raise typer.Exit(1)

    try:
        # Find files
        files = list(directory.glob(pattern))
        if not files:
            console.print(f"[yellow]No files found matching pattern: {pattern}[/yellow]")
            raise typer.Exit(0)

        console.print(f"\n[cyan]Found {len(files)} files to summarize[/cyan]\n")

        # Create summarizer
        summarizer = DocumentSummarizer(llm_type=llm_type, model=model)

        # Process batch
        results = await summarizer.summarize_batch(files, summary_type)

        # Count successes/failures
        successful = sum(1 for r in results if 'error' not in r)
        failed = len(results) - successful

        # Export results
        await summarizer.export_summaries(results, output, format=export_format)

        # Display summary
        console.print(f"\n[green]✓ Batch processing complete[/green]")
        console.print(f"[bold]Successful:[/bold] {successful}/{len(results)}")
        if failed > 0:
            console.print(f"[bold yellow]Failed:[/bold yellow] {failed}/{len(results)}")
        console.print(f"[bold]Output:[/bold] {output}")

    except Exception as e:
        log_error(f"Batch summarization failed: {str(e)}")
        raise typer.Exit(1)


@app.command("types")
def list_types():
    """List available summary types."""
    table = Table(title="Available Summary Types")
    table.add_column("Type", style="cyan")
    table.add_column("Description", style="white")

    types_info = [
        ("brief", "2-3 sentence concise summary"),
        ("structured", "JSON format with sections (contribution, findings, methodology)"),
        ("detailed", "Comprehensive summary with all key details"),
        ("cornell", "Cornell-style notes (ideas, details, questions, summary)"),
        ("tweet", "Ultra-brief summary (280 characters max)"),
    ]

    for type_name, description in types_info:
        table.add_row(type_name, description)

    console.print(table)


if __name__ == "__main__":
    app()
