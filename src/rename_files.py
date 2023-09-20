import os
import signal
import subprocess
import platform
from src.dir_walker import dir_walker
from utils.bcolors import print_info, print_header, print_success
from src.rename_article_or_book import (
    rename_article,
    rename_book,
    rename_thesis,
    rename_commercial_document,
    rename_legal_document,
    rename_nda,
)

from src.constants import DocType

actions = {
    DocType.ARTICLE: rename_article,
    DocType.BOOK: rename_book,
    DocType.THESIS: rename_thesis,
    DocType.COMMERCIAL_DOCUMENT: rename_commercial_document,
    DocType.LEGAL_DOCUMENT: rename_legal_document,
    DocType.NON_DISCLOSURE_AGREEMENT: rename_nda,
}

exclude_project_dir = "_project"


def validate_article(filename):
    return True


def validate_book(filename):
    return True


def validate_thesis(filename):
    return True


validators = {
    DocType.ARTICLE: validate_article,
    DocType.BOOK: validate_book,
    DocType.THESIS: validate_thesis,
    DocType.COMMERCIAL_DOCUMENT: lambda x: True,
    DocType.LEGAL_DOCUMENT: lambda x: True,
    DocType.NON_DISCLOSURE_AGREEMENT: lambda x: True,
}


def contains_document_type(filename):
    for doc_type in DocType.get_type_ext_docs():
        if "." + doc_type + "." in filename:
            # Add validation for the rest of the filename
            validated = validators[doc_type](filename)
            return True
    return False


def get_filename(file):
    return os.path.basename(file)


def set_filename(option, file, filename):
    return actions[DocType.get_type_ext_docs()[option - 1]](file, get_extension(filename))


def get_extension(filename):
    return os.path.splitext(filename)[1]


def open_file(file):
    print_info(f"Opening file: {file}")
    if platform.system() == "Linux":
        cmd = ["xdg-open", file]
    elif platform.system() == "Darwin":
        cmd = ["open", file]
    elif platform.system() == "Windows":
        cmd = ["start", file]
    else:
        raise OSError("Unsupported operating system")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        shell=True if platform.system() == "Windows" else False,
    )
    return process


def close_file(process):
    if platform.system() in ("Linux", "Darwin"):
        os.kill(process.pid, signal.SIGTERM)
    elif platform.system() == "Windows":
        process.terminate()
    else:
        raise OSError("Unsupported operating system")


def show_options(filename):
    print_header(f"Select an document type for {filename}:")
    for i in range(DocType.total_types()):
        print_info(f"{i + 1}. {DocType.get_type_docs()[i]}")
    print_info(f"{DocType.total_types()+1}. Delete file")
    print_info(f"{DocType.total_types()+2}. Exit")


def delete_file(file):
    sure = str(input("Are you sure? [yes/no] ")).lower()
    while sure not in ["yes", "y", "no", "n"]:
        sure = str(input("Are you sure? [yes/no] ")).lower()
    if sure == "yes" or sure == "y":
        os.remove(file)


def rename_all_files(dir_path):
    print_header("Starting rename files...")
    for file in dir_walker(dir_path, dir_excludes=[exclude_project_dir]):
        filename = get_filename(file)
        if contains_document_type(filename):
            continue
        process = open_file(file)
        show_options(filename)
        option = int(input("Option: "))
        while option not in range(1, DocType.total_types() + 3):
            option = int(input("Option: "))
        if option == DocType.total_types() + 1:
            close_file(process)
            delete_file(file)
            continue
        elif option == DocType.total_types() + 2:
            close_file(process)
            print_info("Exiting...")
            break
        close_file(process)
        renamed = set_filename(option, file, filename)
        while not renamed:
            renamed = set_filename(option, file, filename)
        print_success("File renamed successfully!")
    print_success("Finished renaming files!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python rename_files.py <dir> <new_name>")
        sys.exit(1)
    rename_all_files(sys.argv[1])
