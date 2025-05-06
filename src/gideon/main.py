import asyncio
from pathlib import Path
import typer
from rich.console import Console
from rich.tree import Tree
from pypdf import PdfReader

console = Console()
app = typer.Typer(help="Gideon CLI - AI-CLI for file organization")

renaming_app = typer.Typer(
    help="Renaming files using AI and other methods",
)

app.add_typer(
    renaming_app, name="rename", help="Renaming files using AI and other methods"
)


@renaming_app.command("auto")
def rename_file(
    directory: Path = typer.Argument(..., help="Directory containing files for rename"),
):
    asyncio.run(rename_files_with_ai(directory))


# TODO: Move this to a separate module
def _extract_pdf_content(file_path: Path) -> str:
    try:
        reader = PdfReader(str(file_path))
        meta = reader.metadata
        if meta:
            console.print(f"[green]Metadata for {file_path.name}: {meta}[/green]")
        else:
            console.print(f"[yellow]No metadata found for {file_path.name}[/yellow]")

        content = []
        for page in reader.pages[:3]:
            content.append(page.extract_text())
        return "\n".join(content)
    except Exception as e:
        console.print(f"[red]Error reading PDF file {file_path.name}: {e}[/red]")
        return ""


async def _rename_file(file_path: Path) -> str | None:
    try:
        content = _extract_pdf_content(file_path)
        if not content:
            console.print(f"[yellow]No content extracted from {file_path.name}[/yellow]")
            return None
        console.print(f"[green]Extracted content from {file_path.name}:[/green]")
        console.print(content)
    except Exception as e:
        console.print(f"[red]Error extracting content from {file_path}: {e}[/red]")
        return None


async def rename_files_with_ai(directory: Path):
    console.print(f"Renaming files in {directory} using AI...")
    console.print(_directory_tree(directory))
    files = list(directory.rglob("*.pdf"))
    if not files:
        console.print("[yellow]No files found in the directory.[/yellow]")
        return
    console.print(f"Found {len(files)} PDF files to rename.")
    for file_path in files:
        console.print(f"Processing file: {file_path.name}")
        new_name = await _rename_file(file_path)
        console.print(f"New name: {new_name}")


# TODO: Move this to a separate module
def _directory_tree(directory: Path) -> Tree:
    tree = Tree(f"[bold magenta]{directory.name}[/bold magenta]")
    for item in directory.iterdir():
        if item.is_dir():
            subtree = _directory_tree(item)
            tree.add(subtree)
        else:
            if item.suffix in [".pdf"]:
                tree.add(f"[blue]{item.name}[/blue]")
            else:
                tree.add(f"[red]{item.name}[/red]")
    return tree


if __name__ == "__main__":
    app()
