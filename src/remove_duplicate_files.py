import hashlib
import os
from pathlib import Path
from src.dir_walker import dir_walker



def remove_duplicate_files(dir_path, auto_delete=False):
    seen = set()
    for file in dir_walker(Path(dir_path)):
        with open(file, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        if file_hash in seen:
            if auto_delete:
                os.remove(file)
            else:
                print(f"Duplicate file: {file}")
                intent = str(input("Remove? [yes/no] ")).lower()
                while intent not in ["yes", "no"]:
                    intent = input("Remove? [yes/no] ")
                if intent == "yes":
                    os.remove(file)
        else:
            seen.add(file_hash)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python remove_duplicate_files.py <dir>")
        sys.exit(1)
    remove_duplicate_files(sys.argv[1])
