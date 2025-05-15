import asyncio
from pathlib import Path
import re
import warnings

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
except ImportError:
    print("Installing required packages...")
    raise ImportError("Please install required packages: typer[all] rich")

from .langchain_integration.agent import DocumentAgent
from .dir_walker import DirectoryWalker
from .rename_files import rename_file, show_options, validate_filename
from .delete_duplicated_files import find_duplicates
from .constants import DocType
from .langchain_integration.renaming_agents import renaming_agent
from PyPDF2 import PdfReader

# Suppress PyPDF2 warnings
warnings.filterwarnings('ignore', category=UserWarning, module='PyPDF2')

console = Console()
app = typer.Typer(help="Gideon - Intelligent Document Organization System")

# Create command groups
organize_app = typer.Typer(
    help="Organize documents using AI or manual processing",
    rich_help_panel="Document Organization"
)
rename_app = typer.Typer(
    help="Rename files according to document type",
    rich_help_panel="File Renaming"
)
duplicates_app = typer.Typer(
    help="Find and manage duplicate files",
    rich_help_panel="Duplicate Management"
)

# Add command groups to main app
app.add_typer(organize_app, name="organize", help="Organize documents")
app.add_typer(rename_app, name="rename", help="Rename files")
app.add_typer(duplicates_app, name="duplicates", help="Manage duplicates")

def process_manual(directory: Path):
    """Process files manually using the existing system."""
    dir_walker = DirectoryWalker(directory)
    for file in dir_walker.walk():
        # Process each file as needed
        pass

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
    
    console.print("\n[cyan]Initializing document agent...[/cyan]")
    agent = DocumentAgent(str(directory))
    
    console.print("\n[cyan]Starting document processing...[/cyan]")
    results = await agent.process_directory()
    
    if not results:
        console.print(
            "\n[red]No documents were processed. "
            "Check if there are any supported files in the directory.[/red]"
        )
        return
    
    # Display results in a table
    table = Table(title="Document Processing Results")
    table.add_column("Original Name", style="cyan")
    table.add_column("New Location", style="green")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="yellow")
    
    success_count = 0
    duplicate_count = 0
    error_count = 0
    
    console.print("\n[cyan]Processing results:[/cyan]")
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

@organize_app.command(name="process")
def process_directory(
    directory: Path = typer.Argument(
        ...,
        help="Directory containing files to organize",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True
    ),
    automated: bool = typer.Option(
        True,
        "--automated/--manual",
        "-a/-m",
        help="Use automated processing with LangChain and Ollama (default) or manual processing"
    ),
    auto_delete: bool = typer.Option(
        False,
        "--auto-delete/--no-auto-delete",
        "-d/-D",
        help="Automatically delete duplicate files during processing"
    )
) -> None:
    """
    Organize documents in a directory, either manually or automatically using LLM.
    
    The automated mode uses LangChain and Ollama to intelligently classify and organize documents.
    The manual mode allows you to review and approve each file's classification.
    
    Examples:
        gideon organize process /path/to/documents
        gideon organize process /path/to/documents --manual
        gideon organize process /path/to/documents --auto-delete
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

def _extract_pdf_content(file_path: Path) -> str:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(str(file_path))
        content = []
        # Only read first 3 pages for analysis
        for page in reader.pages[:3]:
            content.append(page.extract_text())
        return "\n".join(content)
    except Exception as e:
        console.print(f"[red]Error reading PDF {file_path.name}: {str(e)}[/red]")
        return ""

async def _rename_file(file_path: Path, supervised: bool) -> str | None:
    """Rename a single file using the renaming agent."""
    try:
        # Extract content
        content = _extract_pdf_content(file_path)
        if not content:
            return None
            
        # Analyze document
        doc_info = await renaming_agent.analyze_document(content, file_path.name)
        if not doc_info:
            return None
            
        # Generate new filename
        new_name = renaming_agent.generate_filename(doc_info)
        
        # If in supervised mode, ask for confirmation
        if supervised:
            console.print(f"\nSuggested name: [green]{new_name}[/green]")
            if not typer.confirm("Accept this name?"):
                return None
                
        return new_name
        
    except Exception as e:
        console.print(f"[red]Error processing {file_path.name}: {str(e)}[/red]")
        return None

@rename_app.command("auto")
def rename_auto(
    directory: Path = typer.Argument(..., help="Directory containing files to rename"),
    supervised: bool = typer.Option(False, "--supervised", "-s", help="Supervised renaming mode")
):
    """Rename files automatically based on their content."""
    asyncio.run(_rename_auto_impl(directory, supervised))

async def _rename_auto_impl(directory: Path, supervised: bool):
    """Implementation of the rename auto command."""
    console.print("\nStarting automated file renaming...")
    
    # Show initial directory structure
    console.print("\nInitial directory structure:")
    console.print(_create_directory_tree(directory))
    
    # Get all PDF files
    files = list(directory.rglob("*.pdf"))
    if not files:
        console.print("[yellow]No PDF files found in the directory[/yellow]")
        return
        
    console.print(f"\nFound {len(files)} PDF files to rename")
    
    # Process files with progress bar
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    )
    
    results = []
    with progress:
        task = progress.add_task("Renaming files...", total=len(files))
        
        for file_path in files:
            progress.update(task, description=f"Processing {file_path.name}")
            
            new_name = await _rename_file(file_path, supervised)
            if new_name:
                try:
                    new_path = file_path.parent / new_name
                    file_path.rename(new_path)
                    results.append({
                        "original": file_path.name,
                        "new": new_name,
                        "success": True
                    })
                except Exception as e:
                    results.append({
                        "original": file_path.name,
                        "error": str(e),
                        "success": False
                    })
            else:
                results.append({
                    "original": file_path.name,
                    "error": "Failed to generate new name",
                    "success": False
                })
            
            progress.update(task, advance=1)
    
    # Show results
    table = Table(title="Renaming Results")
    table.add_column("Original Name", style="cyan")
    table.add_column("New Name", style="green")
    table.add_column("Status", style="yellow")
    
    for result in results:
        if result["success"]:
            table.add_row(result["original"], result["new"], "✓")
        else:
            table.add_row(result["original"], "-", f"✗ {result['error']}")
    
    console.print("\nFinal directory structure:")
    console.print(_create_directory_tree(directory))
    console.print(table)

@rename_app.command(name="process")
def rename_directory(
    directory: Path = typer.Argument(
        ...,
        help="Directory containing files to rename",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True
    )
) -> None:
    """
    Rename files in a directory according to their document type.
    
    This command will:
    1. Scan the directory for files
    2. For each file, prompt you to select a document type
    3. Guide you through providing the necessary metadata
    4. Rename the file according to the selected format
    
    Examples:
        gideon rename process /path/to/documents
    """
    if not directory.exists():
        console.print(f"[red]Directory {directory} does not exist[/red]")
        raise typer.Exit(1)
        
    try:
        for file_path in directory.glob("**/*"):
            if file_path.is_file() and file_path.suffix in [".pdf", ".txt"]:
                if validate_filename(file_path.name):
                    console.print(f"[green]File {file_path.name} is already properly named[/green]")
                else:
                    show_options(file_path.name)
                    choice = int(input("Enter your choice: "))
                    if choice <= DocType.total_types():
                        doc_type = DocType.get_type_ext_docs()[choice - 1]
                        rename_file(file_path, doc_type)
                    elif choice == DocType.total_types() + 1:
                        file_path.unlink()
                        console.print(f"[red]Deleted file: {file_path.name}[/red]")
                    else:
                        console.print("[yellow]Skipping file rename[/yellow]")
    except Exception as e:
        console.print(f"[red]Error during renaming: {str(e)}[/red]")
        raise typer.Exit(1)

@duplicates_app.command(name="find")
def find_duplicates_command(
    directory: Path = typer.Argument(
        ...,
        help="Directory to search for duplicates",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True
    ),
    auto_delete: bool = typer.Option(
        False,
        "--auto-delete/--no-auto-delete",
        "-d/-D",
        help="Automatically delete duplicate files"
    )
) -> None:
    """
    Find and optionally delete duplicate files in a directory.
    
    This command will:
    1. Scan the directory for files
    2. Calculate file hashes to identify duplicates
    3. Show a list of duplicate files
    4. Optionally delete duplicates if --auto-delete is specified
    
    Examples:
        gideon duplicates find /path/to/documents
        gideon duplicates find /path/to/documents --auto-delete
    """
    if not directory.exists():
        console.print(f"[red]Directory {directory} does not exist[/red]")
        raise typer.Exit(1)
        
    try:
        duplicates = find_duplicates(directory)
        if not duplicates:
            console.print("[green]No duplicate files found[/green]")
            return
            
        table = Table(title="Duplicate Files")
        table.add_column("Original", style="cyan")
        table.add_column("Duplicate", style="yellow")
        table.add_column("Status", style="magenta")
        
        for original, duplicate in duplicates:
            if auto_delete:
                try:
                    duplicate.unlink()
                    status = "✓ Deleted"
                except Exception as e:
                    status = f"✗ Failed to delete: {str(e)}"
            else:
                status = "⚠ Found"
            table.add_row(str(original.relative_to(directory)), str(duplicate.relative_to(directory)), status)
            
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error finding duplicates: {str(e)}[/red]")
        raise typer.Exit(1)

def normalize_filename(filename: str) -> str:
    """Normalize a filename to follow our standard format."""
    # Remove any extra spaces and normalize dots
    filename = re.sub(r'\s+', ' ', filename).strip()
    filename = re.sub(r'\.+', '.', filename)
    
    # Split into parts
    parts = filename.split('.')
    if len(parts) < 2:
        return filename
        
    # Normalize each part
    normalized_parts = []
    for i, part in enumerate(parts):
        if i == 0:  # Author name
            # Handle multiple authors
            authors = [a.strip().capitalize() for a in part.split('_')]
            normalized_parts.append('_'.join(authors))
        elif i == 1:  # Year
            # Ensure year is 4 digits
            year = re.sub(r'\D', '', part)
            if len(year) == 2:
                year = '20' + year if int(year) < 50 else '19' + year
            normalized_parts.append(year)
        else:  # Title, topic, etc.
            # Capitalize words and remove special characters
            words = [w.capitalize() for w in re.sub(r'[^a-zA-Z0-9\s]', ' ', part).split()]
            normalized_parts.append(''.join(words))
    
    # Ensure we have at least Author.Year.Title.Topic
    while len(normalized_parts) < 4:
        normalized_parts.append('Unknown')
    
    return '.'.join(normalized_parts) + '.pdf'

if __name__ == "__main__":
    app()
