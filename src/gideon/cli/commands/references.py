"""CLI commands for reference extraction."""

from pathlib import Path
from typing import Optional
import asyncio

import typer
from rich.console import Console
from rich.table import Table

from ...services.reference_extractor import ReferenceExtractor
from ...llm.factory import LLMServiceType
from ...utils.logging import log_error

app = typer.Typer(help="Extract references and citations from documents")
console = Console()


@app.command("extract")
def extract_references(
    file_path: Path = typer.Argument(..., help="Path to document"),
    use_llm: bool = typer.Option(True, "--llm/--no-llm", help="Use LLM for extraction"),
    llm_type: Optional[LLMServiceType] = typer.Option(None, "--llm-type", help="LLM service"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("bibtex", "--format", "-f", help="Format (bibtex, apa, json)"),
):
    """Extract references from a document."""
    asyncio.run(_extract_references(file_path, use_llm, llm_type, output, format))


async def _extract_references(
    file_path: Path,
    use_llm: bool,
    llm_type: Optional[LLMServiceType],
    output: Optional[Path],
    format: str
):
    """Async implementation."""
    try:
        extractor = ReferenceExtractor(llm_type=llm_type)
        references = await extractor.extract_from_file(file_path, use_llm=use_llm)

        # Display
        console.print(f"\n[green]✓ Found {len(references)} references[/green]\n")

        table = Table(title="Extracted References")
        table.add_column("#", style="cyan")
        table.add_column("Authors", style="white")
        table.add_column("Title", style="yellow")
        table.add_column("Year", style="green")

        for i, ref in enumerate(references[:10], 1):  # Show first 10
            authors = ", ".join(ref.authors[:2]) if ref.authors else "Unknown"
            if len(ref.authors) > 2:
                authors += " et al."
            table.add_row(str(i), authors, ref.title[:60], ref.year or "")

        console.print(table)

        if len(references) > 10:
            console.print(f"[dim]... and {len(references) - 10} more[/dim]\n")

        # Export
        if output:
            await extractor.export_references(references, output, format=format)
            console.print(f"[green]✓ Exported to {output}[/green]")

    except Exception as e:
        log_error(f"Extraction failed: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
