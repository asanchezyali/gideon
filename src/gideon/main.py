import asyncio
from pathlib import Path
import typer
from rich.console import Console

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
    directory: Path = typer.Argument(..., help="Directory containing files for rename")
):
    asyncio.run(rename_files_with_ai(directory))
    

async def rename_files_with_ai(directory: Path):
    console.print(f"Renaming files in {directory} using AI...")


if __name__ == "__main__":
    app()