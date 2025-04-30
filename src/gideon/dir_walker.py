import os
import sys
from pathlib import Path
from typing import List, Optional, Iterator


class DirWalker:
    def __init__(
        self,
        dir_excludes: Optional[List[str]] = None,
        file_excludes: Optional[List[str]] = None
    ):
        self.dir_excludes = dir_excludes or []
        self.file_excludes = file_excludes or []

    def process_directory(self, dir_path: str) -> Iterator[str]:
        """Process a directory and yield file paths."""
        for root, _, files in os.walk(dir_path):
            path_parts = root.split(os.sep)
            
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
                if file.endswith((".pdf", ".txt")):
                    yield os.path.join(root, file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dir_walker.py <dir>")
        sys.exit(1)

    walker = DirWalker()
    for file in walker.process_directory(sys.argv[1]):
        print(file)
