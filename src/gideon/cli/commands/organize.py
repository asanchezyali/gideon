import typer
from pathlib import Path
from ...services.file_service import FileService

organize_app = typer.Typer(help="Organize files into folders based on AI analysis")


@organize_app.callback(invoke_without_command=True)
def organize(
    directory: Path = typer.Argument(..., help="Directory containing files to organize"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Perform a dry run without making changes"),
    ignore: str = typer.Option(
        None, 
        "--ignore", 
        "-i", 
        help="Comma-separated list of directory patterns to ignore (e.g. '.git,.vscode,node_modules')"
    ),
):
    """
    Organize files into topic-based folders and clean up empty directories.
    
    The organization is based on the file naming convention where topics are extracted
    from filenames in the format: name.topic.extension
    """
    # Convert comma-separated string to list if provided
    ignore_patterns = ignore.split(",") if ignore else None
    
    FileService.organize_files(directory, dry_run, ignore_patterns)
