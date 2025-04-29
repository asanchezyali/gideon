import asyncio
from pathlib import Path

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
except ImportError:
    print("Installing required packages...")
    raise ImportError("Please install required packages: typer[all] rich")

from .langchain_integration.agent import DocumentAgent
from .dir_walker import DirWalker

console = Console()
app = typer.Typer()

def process_manual(directory: Path):
    """Process files manually using the existing system."""
    dir_walker = DirWalker()
    dir_walker.process_directory(directory)

def _create_directory_tree(directory: Path) -> Tree:
    """Create a tree visualization of the directory structure."""
    tree = Tree(f"📁 {directory.name}")
    
    # Add subdirectories
    for path in sorted(directory.iterdir()):
        if path.is_dir() and not path.name.startswith('.'):
            branch = tree.add(f"📁 {path.name}")
            file_count = len([f for f in path.glob('*') if f.is_file()])
            if file_count > 0:
                branch.add(f"📄 {file_count} {'file' if file_count == 1 else 'files'}")
    
    return tree

async def process_automated(directory: Path, auto_delete: bool = False) -> None:
    """Process files automatically using LangChain and Ollama."""
    console.print("\n[yellow]Starting automated document processing...[/yellow]")
    
    # Show initial directory state
    console.print("\n[blue]Initial directory structure:[/blue]")
    console.print(_create_directory_tree(directory))
    
    agent = DocumentAgent(str(directory))
    results = await agent.process_directory()
    
    # Display results in a table
    table = Table(title="Document Processing Results")
    table.add_column("Original Name", style="cyan")
    table.add_column("New Location", style="green")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="yellow")
    
    success_count = 0
    duplicate_count = 0
    error_count = 0
    
    for result in results:
        if result.get("is_duplicate", False):
            original = Path(result["file_path"]).name
            duplicate_count += 1
            if auto_delete:
                try:
                    Path(result["file_path"]).unlink()
                    status = "✓ Duplicate removed"
                except Exception as e:
                    status = f"✗ Failed to remove duplicate: {str(e)}"
            else:
                status = "⚠ Duplicate found"
            table.add_row(original, "N/A", "DUPLICATE", status, style="yellow")
        elif result["success"]:
            success_count += 1
            original = Path(result["original_path"]).name
            new_path = Path(result["new_filename"])
            doc_type = result["classification"]["doc_type"]
            confidence = result["classification"]["confidence"]
            status = f"✓ ({confidence:.0%} confident)"
            table.add_row(original, str(new_path.relative_to(directory)), doc_type, status)
        else:
            error_count += 1
            original = Path(result["file_path"]).name
            status = f"✗ ({result['error']})"
            table.add_row(original, "N/A", "ERROR", status, style="red")
    
    console.print("\n[yellow]Processing complete![/yellow]")
    console.print(table)
    
    # Show summary
    summary = Panel(
        f"""[green]Successfully processed: {success_count}[/green]
[yellow]Duplicates found: {duplicate_count}[/yellow]
[red]Errors: {error_count}[/red]""",
        title="Processing Summary",
        expand=False
    )
    console.print(summary)
    
    # Show final directory structure
    console.print("\n[blue]Final directory structure:[/blue]")
    console.print(_create_directory_tree(directory))

@app.command()
def organize_files(
    directory: Path = typer.Argument(..., help="Directory containing files to organize"),
    automated: bool = typer.Option(
        True,
        help="Use automated processing with LangChain and Ollama"
    ),
    auto_delete: bool = typer.Option(
        False,
        help="Automatically delete duplicate files"
    )
) -> None:
    """
    Organize documents in a directory, either manually or automatically using LLM.
    """
    if not directory.exists():
        console.print(f"[red]Directory {directory} does not exist[/red]")
        raise typer.Exit(1)
        
    try:
        if automated:
            console.print("[yellow]Using automated processing with LangChain and Ollama[/yellow]")
            asyncio.run(process_automated(directory, auto_delete))
        else:
            console.print("[yellow]Using manual processing[/yellow]")
            process_manual(directory)
            
        console.print("\n[green]Processing completed successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error during processing: {str(e)}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
