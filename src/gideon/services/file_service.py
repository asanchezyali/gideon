from pathlib import Path
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader
from rich.tree import Tree
import hashlib
from ..core.config import settings
from ..utils.bcolors import print_success, print_error


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
            print_error(f"Error reading PDF file {file_path.name}: {e}")
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
                print_success(f"Renamed: {file_path.name} -> {new_name}")
                return new_path
            return file_path
        except Exception as e:
            print_error(f"Error renaming {file_path}: {str(e)}")
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

    @staticmethod
    def remove_duplicates(directory: Path) -> None:
        files = FileService.get_files_by_extension(directory)
        visited_files = set()
        removed_files = 0
        for file in files:
            file_hash = hashlib.sha256(file.read_bytes()).hexdigest()
            if file_hash in visited_files:
                file.unlink()
                print_success(f"Removed: {file.name}")
                removed_files += 1
            else:
                visited_files.add(file_hash)
        print_success(f"Removed {removed_files} duplicate files")
