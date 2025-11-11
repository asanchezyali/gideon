"""Interactive chat with research assistant."""

import asyncio
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from ...search.semantic_search import SemanticSearchEngine
from ...llm.factory import LLMServiceFactory
from ...core.config import settings
from ...utils.logging import log_error

console = Console()
chat_app = typer.Typer(help="Interactive research assistant chat")


@chat_app.callback(invoke_without_command=True)
def chat():
    """
    Interactive chat with your document collection.

    Ask questions, search documents, and get AI-powered insights.
    """
    asyncio.run(_chat())


async def _chat():
    """Async chat implementation."""
    console.print(Panel.fit(
        "[bold cyan]Gideon Research Assistant[/bold cyan]\n\n"
        "Ask questions about your document collection.\n"
        "Type 'help' for commands, 'quit' to exit.",
        border_style="cyan"
    ))

    # Initialize search engine
    search_engine = SemanticSearchEngine()

    # Check if documents are indexed
    stats = search_engine.get_statistics()
    if stats['total_chunks'] == 0:
        console.print("\n[yellow]⚠ No documents indexed yet![/yellow]")
        console.print("Run: [cyan]gideon search index <directory>[/cyan]\n")
        return

    console.print(f"\n[dim]Indexed: {stats['total_chunks']} chunks[/dim]\n")

    # Chat loop
    while True:
        try:
            # Get user input
            console.print("[bold]You:[/bold] ", end="")
            user_input = input().strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("\n[cyan]Goodbye! 👋[/cyan]\n")
                break

            elif user_input.lower() == 'help':
                console.print(Panel(
                    "[bold]Commands:[/bold]\n\n"
                    "• [cyan]quit/exit[/cyan] - Exit chat\n"
                    "• [cyan]help[/cyan] - Show this message\n"
                    "• [cyan]stats[/cyan] - Show index statistics\n"
                    "• Ask any question about your documents!",
                    title="Help",
                    border_style="blue"
                ))
                continue

            elif user_input.lower() == 'stats':
                console.print(Panel(
                    f"[bold]Index Statistics:[/bold]\n\n"
                    f"• Total chunks: {stats['total_chunks']}\n"
                    f"• Status: {stats['status']}\n"
                    f"• Location: {stats['persist_directory']}",
                    title="Statistics",
                    border_style="blue"
                ))
                continue

            # Process question
            console.print("\n[yellow]Thinking...[/yellow]")

            result = await search_engine.ask(user_input, k=3)

            # Display answer
            console.print()
            console.print(Panel(
                Markdown(result['answer']),
                title=f"[bold]Gideon[/bold] (confidence: {result['confidence']:.1%})",
                border_style="green"
            ))

            # Show sources
            if result.get('sources'):
                console.print("\n[dim]Sources:[/dim]")
                for i, source in enumerate(result['sources'][:3], 1):
                    console.print(
                        f"  {i}. [blue]{source.metadata['filename']}[/blue] "
                        f"({source.similarity_score:.1%})"
                    )

            console.print()

        except KeyboardInterrupt:
            console.print("\n\n[cyan]Goodbye! 👋[/cyan]\n")
            break
        except Exception as e:
            log_error(f"Chat error: {e}")
            console.print(f"\n[red]Error: {e}[/red]\n")
