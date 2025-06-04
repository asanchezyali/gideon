import asyncio
from pathlib import Path
import typer
from rich.console import Console

from ...agents.renamer import RenameWizard
from ...services.file_service import FileService
from ...core.config import settings
from ...llm.factory import LLMServiceType

console = Console()
rename_app = typer.Typer(help="Renaming files using AI and other methods")


@rename_app.command("auto")
def rename_file(
    directory: Path = typer.Argument(..., help="Directory containing files for rename"),
    llm_service_type: LLMServiceType = typer.Option(
        settings.DEFAULT_LLM_SERVICE_TYPE,
        help="Type of LLM to use for analysis",
    ),
    model: str = typer.Option(
        settings.DEFAULT_LLM_CONFIG["model"],
        help="Model name to use",
    ),
    temperature: float = typer.Option(
        settings.DEFAULT_LLM_CONFIG["temperature"],
        help="Temperature for LLM responses",
    ),
):
    """Rename files in a directory using AI analysis."""
    asyncio.run(rename_files_with_ai(directory, llm_service_type, model, temperature))


async def rename_files_with_ai(
    directory: Path,
    llm_service_type: LLMServiceType,
    model: str,
    temperature: float,
):
    console.print(f"Renaming files in {directory} using AI...")
    console.print(f"Using LLM service type: {llm_service_type}, model: {model}, temperature: {temperature}")

    # Initialize services
    file_service = FileService()
    console.print(file_service.create_directory_tree(directory))

    # Get files to process
    files = file_service.get_files_by_extension(directory, ".pdf")
    if not files:
        console.print("[yellow]No PDF files found in the directory.[/yellow]")
        return

    console.print(f"Found {len(files)} PDF files to rename.")

    # Initialize rename wizard
    config = {
        "model": model,
        "temperature": temperature,
    }
    rename_wizard = RenameWizard(llm_service_type=llm_service_type, service_config=config)

    # Process files
    async def process_file(file_path: Path) -> None:
        content = await file_service.extract_pdf_content(file_path)
        if not content:
            return

        doc_info = await rename_wizard.rename_document(content, file_path.name)
        if not doc_info:
            return

        new_name = rename_wizard.generate_filename(doc_info)
        file_service.rename_file(file_path, new_name)

    # Process all files concurrently
    tasks = [process_file(file_path) for file_path in files]
    await asyncio.gather(*tasks)
