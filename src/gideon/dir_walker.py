"""Directory walker for processing files."""
import os
import sys
from pathlib import Path
from typing import List, Optional, Iterator

class DirectoryWalker:
    """Walk through directories and process files."""
    
    def __init__(
        self,
        directory: Path,
        dir_excludes: Optional[List[str]] = None,
        file_excludes: Optional[List[str]] = None
    ):
        """Initialize DirectoryWalker.
        
        Args:
            directory: Base directory path to process
            dir_excludes: List of directory patterns to exclude
            file_excludes: List of file patterns to exclude
        """
        self.directory = directory
        self.dir_excludes = dir_excludes or []
        self.file_excludes = file_excludes or []

    def walk(self) -> Iterator[Path]:
        """Walk through the directory and yield file paths.
        
        Returns:
            Iterator of Path objects for matching files
        """
        for root, _, files in os.walk(self.directory):
            path_parts = Path(root).parts
            
            # Skip excluded directories
            if any(
                part.endswith(dir_exclude)
                for part in path_parts
                for dir_exclude in self.dir_excludes
            ):
                continue
                
            # Filter excluded files
            if self.file_excludes:
                files = [
                    file
                    for file in files
                    if not any(
                        file.endswith(file_exclude)
                        for file_exclude in self.file_excludes
                    )
                ]

            for file in files:
                # Skip system files
                if file.startswith("._"):
                    continue
                    
                # Only process supported file types
                if file.lower().endswith((".pdf", ".txt", ".djvu")):
                    yield Path(root) / file


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dir_walker.py <dir>")
        sys.exit(1)

    walker = DirectoryWalker(Path(sys.argv[1]))
    for file in walker.walk():
        print(file)
