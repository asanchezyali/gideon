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
            content = reader.load()
            metadata = content[0].metadata if content else {}
            print(metadataj)
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

    @staticmethod
    def organize_files(directory: Path, dry_run: bool = False, ignore_patterns: list = None) -> None:
        """Organize files into topic-based subdirectories and delete empty directories.
        
        Args:
            directory: The root directory to organize
            dry_run: If True, only show what would be done without making changes
            ignore_patterns: List of directory patterns to ignore (e.g., ['.git', '.vscode'])
        """
        if ignore_patterns is None:
            ignore_patterns = ['.git', '.svn', '__pycache__', '.vscode', '.idea', 'node_modules']
            
        # Get all files matching the extension pattern
        files = FileService.get_files_by_extension(directory)
        organized_count = 0
        skipped_count = 0
        
        for file in files:
            # Skip files in ignored directories
            if any(pattern in str(file) for pattern in ignore_patterns):
                continue
                
            # Skip files with insufficient topic information
            if len(file.stem.split(".")) < 3:
                print_error(f"Skipping file with insufficient topic information: {file.name}")
                skipped_count += 1
                continue
                
            # Extract topic from filename
            topic = file.stem.split(".")[-2]
            target_dir = directory / topic
            
            # Create target directory if it doesn't exist
            if not target_dir.exists():
                if not dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                print_success(f"Created directory: {target_dir}")
                
            # Move file to target directory
            new_path = target_dir / file.name
            if not dry_run and new_path != file:
                try:
                    file.rename(new_path)
                    print_success(f"Moved: {file.name} -> {target_dir.name}/{file.name}")
                    organized_count += 1
                except Exception as e:
                    print_error(f"Error moving file {file.name}: {str(e)}")
            elif dry_run:
                organized_count += 1
                
        # Clean up empty directories
        if not dry_run:
            try:
                FileService._delete_empty_directories(directory, ignore_patterns)
                print_success(f"Deleted empty directories in {directory}")
            except Exception as e:
                print_error(f"Error cleaning up empty directories: {str(e)}")
        else:
            print_success("Dry run completed, no changes made")
            
        # Print summary
        if organized_count == 0:
            print_error("No files were organized")
        else:
            if dry_run:
                print_success(f"Dry run: {organized_count} files would be organized")
            else:
                print_success(f"Organized {organized_count} files into their respective directories")
                
        if skipped_count > 0:
            print_error(f"Skipped {skipped_count} files due to insufficient topic information")

    @staticmethod
    def _delete_empty_directories(directory: Path, ignore_patterns: list = None) -> None:
        """Delete empty directories recursively.
        
        Args:
            directory: The directory to check for empty subdirectories
            ignore_patterns: List of directory name patterns to ignore (e.g., ['.git', '.vscode'])
        """
        if ignore_patterns is None:
            ignore_patterns = ['.git', '.svn', '__pycache__', '.vscode']
            
        # Skip processing for ignored directories
        if any(pattern in str(directory) for pattern in ignore_patterns):
            return
            
        try:
            # Get all subdirectories
            subdirs = [item for item in directory.iterdir() if item.is_dir()]
            
            # Process subdirectories first
            for item in subdirs:
                # Skip ignored directories
                if any(pattern in item.name for pattern in ignore_patterns):
                    continue
                    
                try:
                    FileService._delete_empty_directories(item, ignore_patterns)
                except (PermissionError, FileNotFoundError) as e:
                    print_error(f"Error processing directory {item}: {str(e)}")
            
            # Check if this directory is now empty and can be deleted
            try:
                if directory.exists() and not any(directory.iterdir()):
                    directory.rmdir()
                    print_success(f"Deleted empty directory: {directory}")
            except (PermissionError, FileNotFoundError) as e:
                print_error(f"Error deleting directory {directory}: {str(e)}")
                
        except (PermissionError, FileNotFoundError) as e:
            print_error(f"Error accessing directory {directory}: {str(e)}")
