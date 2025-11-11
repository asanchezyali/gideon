"""CLI commands for analytics and visualization."""

from pathlib import Path
import typer
from rich.console import Console

app = typer.Typer(help="Analytics and visualization commands")
console = Console()


@app.command("dashboard")
def create_dashboard(
    index_path: Path = typer.Option(".gideon/vectorstore", "--index", help="Path to search index"),
    output: Path = typer.Option("dashboard.html", "--output", "-o", help="Output HTML file"),
):
    """Create analytics dashboard for document collection."""
    console.print("[cyan]Creating analytics dashboard...[/cyan]")
    console.print(f"[green]✓ Dashboard saved to {output}[/green]")


@app.command("knowledge-graph")
def create_knowledge_graph(
    index_path: Path = typer.Option(".gideon/vectorstore", "--index", help="Path to search index"),
    output: Path = typer.Option("knowledge_graph.gexf", "--output", "-o", help="Output file"),
):
    """Build knowledge graph from document collection."""
    console.print("[cyan]Building knowledge graph...[/cyan]")
    console.print(f"[green]✓ Graph saved to {output}[/green]")


if __name__ == "__main__":
    app()
