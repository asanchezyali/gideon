"""Smart duplicate detection commands."""

import asyncio
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ...services.duplicate_detector import SmartDuplicateDetector, DuplicateType
from ...services.file_service import FileService
from ...utils.logging import log_success, log_error

console = Console()
deduplicate_app = typer.Typer(help="Smart duplicate detection and removal")


@deduplicate_app.command("scan")
def scan_duplicates(
    directory: Path = typer.Argument(..., help="Directory to scan for duplicates"),
    mode: str = typer.Option("all", "--mode", "-m", help="Detection mode: exact, version, all"),
    auto_remove: bool = typer.Option(False, "--remove", "-r", help="Automatically remove duplicates"),
):
    """
    Scan for duplicate files with intelligent detection.

    Modes:
    - exact: Find identical files (hash-based)
    - version: Find different versions (v1, v2, draft, final)
    - all: Both exact and version detection
    """
    asyncio.run(_scan_duplicates(directory, mode, auto_remove))


async def _scan_duplicates(directory: Path, mode: str, auto_remove: bool):
    """Async implementation of scan command."""
    console.print(f"\n[bold cyan]Scanning for duplicates in:[/bold cyan] {directory}\n")

    # Get files
    file_service = FileService()
    files = file_service.get_files_by_extension(directory, ".pdf")

    if not files:
        console.print("[red]No PDF files found![/red]")
        return

    console.print(f"Found [green]{len(files)}[/green] files to check\n")

    # Determine detection levels
    detection_levels = []
    if mode in ["exact", "all"]:
        detection_levels.append(DuplicateType.EXACT)
    if mode in ["version", "all"]:
        detection_levels.append(DuplicateType.VERSION)

    # Detect duplicates
    console.print("[yellow]Detecting duplicates...[/yellow]")
    detector = SmartDuplicateDetector()
    duplicate_groups = await detector.detect_duplicates(files, detection_levels)

    if not duplicate_groups:
        console.print("\n[green]✓ No duplicates found![/green]")
        return

    # Display results
    console.print(f"\n[bold]Found {len(duplicate_groups)} duplicate groups:[/bold]\n")

    total_duplicates = 0
    total_space_saved = 0

    for i, group in enumerate(duplicate_groups, 1):
        # Create table for this group
        table = Table(
            title=f"Group {i} - {group.duplicate_type.value.upper()}",
            show_header=True,
            border_style="blue"
        )
        table.add_column("Status", style="cyan", width=8)
        table.add_column("File", style="white")
        table.add_column("Size", style="yellow", width=10)

        for file_path in group.files:
            size_mb = file_path.stat().st_size / 1024 / 1024
            status = "KEEP" if file_path == group.primary_file else "REMOVE"
            style = "green" if status == "KEEP" else "red"

            table.add_row(
                f"[{style}]{status}[/{style}]",
                file_path.name,
                f"{size_mb:.2f} MB"
            )

            if file_path != group.primary_file:
                total_duplicates += 1
                total_space_saved += size_mb

        console.print(table)
        console.print()

    # Summary
    console.print(Panel.fit(
        f"[bold]Summary[/bold]\n\n"
        f"  [cyan]Total duplicate files:[/cyan] {total_duplicates}\n"
        f"  [cyan]Potential space saved:[/cyan] {total_space_saved:.2f} MB\n"
        f"  [cyan]Groups found:[/cyan] {len(duplicate_groups)}",
        border_style="green"
    ))

    # Auto-remove if requested
    if auto_remove:
        console.print(f"\n[yellow]Removing duplicates...[/yellow]")
        removed = 0
        failed = 0

        for group in duplicate_groups:
            for file_path in group.get_files_to_remove():
                try:
                    file_path.unlink()
                    console.print(f"  [green]✓[/green] Removed: {file_path.name}")
                    removed += 1
                except Exception as e:
                    console.print(f"  [red]✗[/red] Failed: {file_path.name} - {e}")
                    failed += 1

        console.print(f"\n[green]✓ Removed {removed} duplicate files[/green]")
        if failed > 0:
            console.print(f"[red]✗ Failed to remove {failed} files[/red]")
    else:
        console.print(f"\n[dim]Run with --remove to delete duplicates[/dim]")


@deduplicate_app.command("clean")
def clean_duplicates(
    directory: Path = typer.Argument(..., help="Directory to clean"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Remove all detected duplicates (interactive mode)."""
    if not confirm:
        confirm = typer.confirm(
            "This will remove duplicate files. Are you sure?",
            abort=True
        )

    asyncio.run(_scan_duplicates(directory, "all", auto_remove=True))
