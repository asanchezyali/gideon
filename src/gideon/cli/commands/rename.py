import asyncio
import time
from pathlib import Path
import typer
from rich.console import Console
from rich.progress import Progress

from ...services.rename_service import RenameService
from ...services.file_service import FileService
from ...core.config import settings
from ...llm.factory import LLMServiceType
from ...utils.logging import set_quiet_mode, flush_messages, log_info, log_error, log_success

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
    max_concurrent: int = typer.Option(
        3, 
        "--concurrent", 
        "-c", 
        help="Maximum number of files to process concurrently",
    ),
):
    """Rename files in a directory using AI analysis."""
    asyncio.run(rename_files_with_ai(directory, llm_service_type, model, temperature, max_concurrent))


async def rename_files_with_ai(
    directory: Path,
    llm_service_type: LLMServiceType,
    model: str,
    temperature: float,
    max_concurrent: int = 3,
):
    log_info(f"Renaming files in {directory} using AI...")
    log_info(f"Using LLM service type: {llm_service_type}, model: {model}, temperature: {temperature}")

    file_service = FileService()
    console.print(file_service.create_directory_tree(directory))

    files = file_service.get_files_by_extension(directory, ".pdf")
    if not files:
        log_error("No PDF files found in the directory.")
        return

    log_info(f"Found {len(files)} PDF files to rename.")

    config = {
        "model": model,
        "temperature": temperature,
    }
    rename_wizard = RenameService(llm_service_type=llm_service_type, service_config=config)
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    processed = 0
    renamed = 0
    skipped = 0
    errors = 0
    start_time = time.time()
    
    set_quiet_mode(True)
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Renaming files...", total=len(files))
        current_file_task = progress.add_task("[yellow]Processing:", total=None, visible=True)

        async def process_file(file_path: Path) -> None:
            nonlocal processed, renamed, skipped, errors
            try:
                async with semaphore:
                    # Update the current file being processed
                    progress.update(
                        current_file_task, 
                        description=f"[yellow]Processing: [bold]{file_path.name}[/bold]"
                    )
                    
                    content = await file_service.extract_pdf_content(file_path)
                    if not content:
                        log_error(f"Could not extract content from {file_path.name}")
                        errors += 1
                        progress.update(task, advance=1)
                        return

                    new_name = await rename_wizard.rename_file(content, file_path.name)
                    if not new_name:
                        log_error(f"Could not generate new name for {file_path.name}")
                        errors += 1
                        progress.update(task, advance=1)
                        return

                    # Only rename if the new name is different from current name
                    if new_name != file_path.name:
                        file_service.rename_file(file_path, new_name)
                        renamed += 1
                    else:
                        skipped += 1
                    
                processed += 1
                progress.update(task, advance=1)
            except Exception as e:
                log_error(f"Error processing {file_path.name}: {str(e)}")
                errors += 1
                progress.update(task, advance=1)

        tasks = [process_file(file_path) for file_path in files]
        await asyncio.gather(*tasks)
        
    set_quiet_mode(False)
    flush_messages()
    
    elapsed_time = time.time() - start_time
    log_success(f"Processing completed in {elapsed_time:.2f} seconds")
    log_info(
        f"Total files: {len(files)}, Processed: {processed}, "
        f"Renamed: {renamed}, Skipped: {skipped}, Errors: {errors}"
    )
