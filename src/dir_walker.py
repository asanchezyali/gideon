import os
import sys


def dir_walker(dir_path):
    for root, _, files in os.walk(dir_path):
        for file in files:
            # filter by pdf files
            if file.endswith(".pdf"):
                yield os.path.join(root, file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dir_walker.py <dir>")
        sys.exit(1)
        
    for file in dir_walker(sys.argv[1]):
        print(file)
