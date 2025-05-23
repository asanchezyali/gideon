import typer
from pathlib import Path
from ...services.file_service import FileService

remove_duplicates_app = typer.Typer(help="Remove duplicate files")


@remove_duplicates_app.callback(invoke_without_command=True)
def remove_duplicates(
    directory: Path = typer.Argument(..., help="Directory containing files for remove duplicates"),
):
    FileService.remove_duplicates(directory)
