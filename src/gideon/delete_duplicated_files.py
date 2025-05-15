import hashlib
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from .dir_walker import DirectoryWalker
from .utils.bcolors import print_header, print_info, print_success


def remove_duplicate_files(dir_path: str | Path, auto_delete: bool = False) -> None:
    """Remove duplicate files from a directory.
    
    Args:
        dir_path: Directory to process
        auto_delete: Whether to delete duplicates automatically
    """
    dir_path = Path(dir_path)
    print_header(f"Removing duplicate files in {dir_path}")
    seen = set()
    walker = DirectoryWalker(dir_path)
    
    for file in walker.walk():
        with open(file, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        if file_hash in seen:
            if auto_delete:
                os.remove(file)
            else:
                print_info(f"Found duplicate file: {file}")
                intent = str(input("Remove? [yes/no] ")).lower()
                while intent not in ["yes", "no"]:
                    intent = input("Remove? [yes/no] ")
                if intent == "yes":
                    os.remove(file)
        else:
            seen.add(file_hash)
    print_info("Finished removing duplicate files!")


def find_duplicates(directory: str | Path, dir_excludes: Optional[List[str]] = None) -> List[Tuple[Path, Path]]:
    """Find duplicate files in a directory.
    
    Args:
        directory: Directory to search for duplicates
        dir_excludes: List of directory names to exclude
        
    Returns:
        List of tuples containing (original_file, duplicate_file)
    """
    directory = Path(directory)
    print_header("Starting duplicate files search...")
    
    # Create a dictionary to store file hashes
    file_hashes: Dict[str, Path] = {}
    duplicates: List[Tuple[Path, Path]] = []
    
    # Initialize DirectoryWalker
    walker = DirectoryWalker(directory, dir_excludes=dir_excludes)
    
    # Process each file in the directory
    for file_path in walker.walk():
        try:
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            # Check if we've seen this hash before
            if file_hash in file_hashes:
                duplicates.append((file_hashes[file_hash], file_path))
            else:
                file_hashes[file_hash] = file_path
                
        except Exception as e:
            print_info(f"Error processing {file_path}: {str(e)}")
    
    if duplicates:
        print_success(f"Found {len(duplicates)} duplicate files!")
    else:
        print_success("No duplicate files found!")
        
    return duplicates


def delete_duplicates(directory: str | Path, dir_excludes: Optional[List[str]] = None) -> None:
    """Delete duplicate files in a directory.
    
    Args:
        directory: Directory to search for duplicates
        dir_excludes: List of directory names to exclude
    """
    print_header("Starting duplicate files removal...")
    
    # Find duplicates
    duplicates = find_duplicates(directory, dir_excludes)
    
    # Delete duplicates
    for original, duplicate in duplicates:
        try:
            os.remove(duplicate)
            print_info(f"Removed duplicate: {duplicate}")
        except Exception as e:
            print_info(f"Error removing {duplicate}: {str(e)}")
    
    print_success("Finished removing duplicate files!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python delete_duplicated_files.py <directory>")
        sys.exit(1)
    delete_duplicates(sys.argv[1])
