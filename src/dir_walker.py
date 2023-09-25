import os
import sys


def dir_walker(dir_path, dir_excludes=None, file_excludes=None):
    for root, _, files in os.walk(dir_path):
        path_parts = root.split(os.sep)
        if dir_excludes:
            if any(
                part.endswith(dir_exclude)
                for part in path_parts
                for dir_exclude in dir_excludes
            ):
                continue
        if file_excludes:
            files = [
                file
                for file in files
                if not any(
                    file.endswith(file_exclude) for file_exclude in file_excludes
                )
            ]

        for file in files:
            if file.startswith("._"):
                continue
            if file.endswith(".pdf"):
                yield os.path.join(root, file)
            if file.endswith(".txt"):
                yield os.path.join(root, file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dir_walker.py <dir>")
        sys.exit(1)

    for file in dir_walker(sys.argv[1]):
        print(file)
