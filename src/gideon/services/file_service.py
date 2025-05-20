from pathlib import Path
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader
from rich.console import Console
from rich.tree import Tree

from ..core.config import settings

console = Console()


class FileService:
    
    @staticmethod
    async def extract_pdf_content(file_path: Path) -> str:
        try:
            reader = PyPDFLoader(str(file_path))
            content = []
            async for page in reader.alazy_load():
                content.append(page.page_content)
            return "\n".join(content)
        except Exception as e:
            console.print(f"[red]Error reading PDF file {file_path.name}: {e}[/red]")
            return ""
    
    @staticmethod
    def get_files_by_extension(directory: Path, extension: str = ".pdf") -> List[Path]:
        return list(directory.rglob(f"*{extension}"))
    
    @staticmethod
    def rename_file(file_path: Path, new_name: str) -> Optional[Path]:
        try:
            new_path = file_path.parent / new_name
            if new_path != file_path:
                file_path.rename(new_path)
                console.print(f"[green]Renamed: {file_path.name} -> {new_name}[/green]")
                return new_path
            return file_path
        except Exception as e:
            console.print(f"[red]Error renaming {file_path}: {str(e)}[/red]")
            return None
    
    @staticmethod
    def create_directory_tree(directory: Path) -> Tree:
        tree = Tree(f"[bold magenta]{directory.name}[/bold magenta]")
        for item in directory.iterdir():
            if item.is_dir():
                subtree = FileService.create_directory_tree(item)
                tree.add(subtree)
            else:
                if item.suffix in settings.SUPPORTED_EXTENSIONS:
                    tree.add(f"[blue]{item.name}[/blue]")
                else:
                    tree.add(f"[red]{item.name}[/red]")
        return tree 