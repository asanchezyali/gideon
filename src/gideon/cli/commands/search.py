"""Search commands for semantic search and Q&A."""

import asyncio
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich.markdown import Markdown

from ...search.semantic_search import SemanticSearchEngine
from ...services.file_service import FileService
from ...llm.factory import LLMServiceType
from ...utils.logging import log_info, log_error, log_success

console = Console()
search_app = typer.Typer(help="Semantic search and Q&A over your document collection")


@search_app.command("index")
def index_documents(
    directory: Path = typer.Argument(..., help="Directory containing documents to index"),
    max_concurrent: int = typer.Option(3, "--concurrent", "-c", help="Max concurrent indexing"),
    clear_existing: bool = typer.Option(False, "--clear", help="Clear existing index first"),
):
    """
    Index documents for semantic search.

    This will extract content from all PDFs in the directory and create
    vector embeddings for semantic search.
    """
    asyncio.run(_index_documents(directory, max_concurrent, clear_existing))


async def _index_documents(directory: Path, max_concurrent: int, clear_existing: bool):
    """Async implementation of index command."""
    console.print(f"\n[bold cyan]Indexing documents from:[/bold cyan] {directory}\n")

    # Initialize services
    search_engine = SemanticSearchEngine()
    file_service = FileService()

    # Clear existing index if requested
    if clear_existing:
        console.print("[yellow]Clearing existing index...[/yellow]")
        search_engine.clear_index()

    # Get files
    files = file_service.get_files_by_extension(directory, ".pdf")

    if not files:
        console.print("[red]No PDF files found![/red]")
        return

    console.print(f"Found [green]{len(files)}[/green] PDF files\n")

    # Index with progress bar
    with Progress() as progress:
        task = progress.add_task("[cyan]Indexing documents...", total=len(files))

        def update_progress(file_path: Path, ratio: float):
            progress.update(task, completed=int(ratio * len(files)))

        stats = await search_engine.index_directory(
            directory,
            file_service,
            progress_callback=update_progress,
            max_concurrent=max_concurrent
        )

    # Display results
    console.print()
    console.print(Panel.fit(
        f"[green]✓[/green] Indexing complete!\n\n"
        f"  [cyan]Indexed:[/cyan] {stats['indexed']} documents\n"
        f"  [yellow]Failed:[/yellow] {stats['failed']} documents\n"
        f"  [blue]Chunks:[/blue] {stats['total_chunks']} total chunks",
        title="[bold]Indexing Results[/bold]",
        border_style="green"
    ))

    # Show index statistics
    index_stats = search_engine.get_statistics()
    console.print(f"\n[dim]Index location: {index_stats['persist_directory']}[/dim]")


@search_app.command("search")
def search_documents(
    query: str = typer.Argument(..., help="Search query"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of results to return"),
    topic: Optional[str] = typer.Option(None, "--topic", help="Filter by topic"),
    author: Optional[str] = typer.Option(None, "--author", help="Filter by author"),
    show_preview: bool = typer.Option(True, "--preview/--no-preview", help="Show text preview"),
):
    """
    Search documents semantically.

    Performs semantic similarity search across your indexed documents.
    """
    asyncio.run(_search_documents(query, top_k, topic, author, show_preview))


async def _search_documents(
    query: str,
    top_k: int,
    topic: Optional[str],
    author: Optional[str],
    show_preview: bool
):
    """Async implementation of search command."""
    console.print(f"\n[bold cyan]Searching for:[/bold cyan] {query}\n")

    # Initialize search engine
    search_engine = SemanticSearchEngine()

    # Check if index exists
    stats = search_engine.get_statistics()
    if stats['total_chunks'] == 0:
        console.print("[red]No documents indexed yet![/red]")
        console.print("Run [cyan]gideon search index <directory>[/cyan] first")
        return

    # Build filters
    filters = {}
    if topic:
        filters['topic'] = topic
    if author:
        filters['author'] = author

    # Perform search
    results = await search_engine.search(query, k=top_k, filter_metadata=filters if filters else None)

    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    # Display results in table
    table = Table(title=f"Search Results ({len(results)} matches)", show_header=True)
    table.add_column("#", style="cyan", width=3)
    table.add_column("Document", style="green")
    table.add_column("Similarity", style="yellow", width=10)

    if show_preview:
        table.add_column("Preview", style="dim", max_width=60)

    for i, result in enumerate(results, 1):
        row = [
            str(i),
            result.metadata['filename'],
            f"{result.similarity_score:.1%}"
        ]

        if show_preview:
            preview = result.chunk_text[:150].replace('\n', ' ')
            if len(result.chunk_text) > 150:
                preview += "..."
            row.append(preview)

        table.add_row(*row)

    console.print(table)

    # Show metadata if available
    if topic or author:
        console.print(f"\n[dim]Filtered by: {filters}[/dim]")


@search_app.command("ask")
def ask_question(
    question: str = typer.Argument(..., help="Question to ask"),
    top_k: int = typer.Option(3, "--top-k", "-k", help="Number of relevant documents to consider"),
    show_sources: bool = typer.Option(True, "--sources/--no-sources", help="Show source documents"),
):
    """
    Ask questions about your document collection (RAG).

    Uses Retrieval-Augmented Generation to answer questions based on
    the content of your indexed documents.
    """
    asyncio.run(_ask_question(question, top_k, show_sources))


async def _ask_question(question: str, top_k: int, show_sources: bool):
    """Async implementation of ask command."""
    console.print(f"\n[bold cyan]Question:[/bold cyan] {question}\n")

    # Initialize search engine
    search_engine = SemanticSearchEngine()

    # Check if index exists
    stats = search_engine.get_statistics()
    if stats['total_chunks'] == 0:
        console.print("[red]No documents indexed yet![/red]")
        console.print("Run [cyan]gideon search index <directory>[/cyan] first")
        return

    # Get answer
    console.print("[yellow]Thinking...[/yellow]")
    result = await search_engine.ask(question, k=top_k, return_sources=show_sources)

    # Display answer
    console.print()
    console.print(Panel(
        Markdown(result['answer']),
        title=f"[bold]Answer[/bold] (confidence: {result['confidence']:.1%})",
        border_style="green"
    ))

    # Show sources
    if show_sources and result.get('sources'):
        console.print("\n[bold]Sources:[/bold]")
        for i, source in enumerate(result['sources'], 1):
            console.print(f"  {i}. [green]{source.metadata['filename']}[/green] "
                         f"(similarity: {source.similarity_score:.1%})")


@search_app.command("similar")
def find_similar(
    document: Path = typer.Argument(..., help="Path to document"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of similar documents"),
):
    """
    Find documents similar to a given document.
    """
    asyncio.run(_find_similar(document, top_k))


async def _find_similar(document: Path, top_k: int):
    """Async implementation of similar command."""
    if not document.exists():
        console.print(f"[red]Document not found:[/red] {document}")
        return

    console.print(f"\n[bold cyan]Finding documents similar to:[/bold cyan] {document.name}\n")

    # Initialize search engine
    search_engine = SemanticSearchEngine()

    # Find similar documents
    results = await search_engine.find_similar_documents(document, k=top_k)

    if not results:
        console.print("[yellow]No similar documents found[/yellow]")
        console.print("[dim]Make sure the document has been indexed[/dim]")
        return

    # Display results
    table = Table(title=f"Similar Documents ({len(results)})", show_header=True)
    table.add_column("#", style="cyan", width=3)
    table.add_column("Document", style="green")
    table.add_column("Similarity", style="yellow", width=10)

    for i, result in enumerate(results, 1):
        table.add_row(
            str(i),
            result.metadata['filename'],
            f"{result.similarity_score:.1%}"
        )

    console.print(table)


@search_app.command("stats")
def show_statistics():
    """Show index statistics."""
    search_engine = SemanticSearchEngine()
    stats = search_engine.get_statistics()

    console.print("\n[bold]Search Index Statistics[/bold]\n")
    console.print(f"  [cyan]Total chunks:[/cyan] {stats['total_chunks']}")
    console.print(f"  [cyan]Status:[/cyan] {stats['status']}")
    console.print(f"  [cyan]Location:[/cyan] {stats['persist_directory']}")
    console.print(f"  [cyan]Embedding model:[/cyan] {stats['embedding_model']}\n")


@search_app.command("clear")
def clear_index(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Clear the search index."""
    if not confirm:
        confirm = typer.confirm("Are you sure you want to clear the index?")

    if confirm:
        search_engine = SemanticSearchEngine()
        search_engine.clear_index()
        console.print("[green]✓[/green] Index cleared")
    else:
        console.print("Cancelled")
