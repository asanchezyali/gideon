import hashlib
import os
from pathlib import Path
from src.dir_walker import dir_walker
from utils.bcolors import print_header, print_info


def remove_duplicate_files(dir_path, auto_delete=False):
    print_header(f"Removing duplicate files in {dir_path}")
    seen = set()
    for file in dir_walker(Path(dir_path)):
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


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python remove_duplicate_files.py <dir>")
        sys.exit(1)
    remove_duplicate_files(sys.argv[1])
