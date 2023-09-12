import os
import signal
import subprocess
from src.dir_walker import dir_walker
from utils.bcolors import print_info, print_header, print_success
from src.rename_article_or_book import (
    rename_file,
    rename_article,
    rename_book,
    rename_thesis,
)
from src.rename_invoice_or_report import rename_invoice_or_report_contract
from src.filename_formats import invoice_validator, article_validator
from src.constants import (
    ARTICLE,
    BOOK,
    THESIS,
    COMMERCIAL_DOCUMENT,
    LEGAL_DOCUMENT,
    SCRIPT,
    NON_DISCLOSURE_AGREEMENT,
)

document_types = [
    ARTICLE,
    BOOK,
    THESIS,
    COMMERCIAL_DOCUMENT,
    LEGAL_DOCUMENT,
    SCRIPT,
    NON_DISCLOSURE_AGREEMENT,
]

actions = {
    ARTICLE: rename_article,
    BOOK: rename_book,
    THESIS: rename_thesis,
}


def contains_document_type(filename):
    for doc_type in document_types:
        if "." + doc_type + "." in filename:
            return True
    return False


def get_filename(file):
    return os.path.basename(file)


def set_filename(option, file, filename):
    actions[document_types[option - 1]](file, get_extension(filename))


def get_extension(filename):
    return os.path.splitext(filename)[1]


def open_file(file):
    process = subprocess.Popen(
        ["xdg-open", file], stdout=subprocess.PIPE, preexec_fn=os.setsid
    )
    return process


def close_file(process):
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)


def show_options(filename):
    print_header(f"Select an document type for {filename}:")
    for i in range(len(document_types)):
        print_info(f"{i+1}. {document_types[i]}")
    print_info(f"{len(document_types)+1}. Delete file")
    print_info(f"{len(document_types)+2}. Exit")


def delete_file(file):
    sure = str(input("Are you sure? [yes/no] ")).lower()
    while sure not in ["yes", "y", "no", "n"]:
        sure = str(input("Are you sure? [yes/no] ")).lower()
    if sure == "yes" or sure == "y":
        os.remove(file)


def rename_all_files(dir_path):
    print_header("Starting rename files...")
    for file in dir_walker(dir_path):
        filename = get_filename(file)
        if contains_document_type(filename):
            continue
        process = open_file(file)
        show_options(filename)
        option = int(input("Option: "))
        while option not in range(1, 10):
            option = int(input("Option: "))
        if option == len(document_types) + 1:
            close_file(process)
            delete_file(file)
            continue
        elif option == len(document_types) + 2:
            close_file(process)
            print_info("Exiting...")
            break
        close_file(process)
        renamed = set_filename(option, file, filename)
        while not renamed:
            renamed = set_filename(option, file, filename)
        print_success("File renamed successfully!")
    print_success("Finished renaming files!")


def get_intent(file, extension):
    rename = str(input("Rename? [yes/no/delete/exit] ")).lower()
    while rename not in ["yes", "y", "no", "n", "delete", "exit"]:
        rename = str(input("Rename? [yes/no/delete/exit] ")).lower()
    if rename == "yes" or rename == "y":
        doc_type = str(
            input(
                "Article or book or invoice or report or contract? [article/book/invoice/report/contract] "
            )
        ).lower()
        while doc_type not in ["article", "book", "invoice", "report", "contract"]:
            doc_type = str(
                input(
                    "Article or book or invoice or report or contract? [article/book/invoice/report/contract] "
                )
            ).lower()
        if doc_type == "article" or doc_type == "book":
            renamed = rename_file(doc_type, file, extension)
            while not renamed:
                renamed = rename_file(doc_type, file, extension)
        elif doc_type == "invoice" or doc_type == "report" or doc_type == "contract":
            renamed = rename_invoice_or_report_contract(doc_type, file, extension)
            while not renamed:
                renamed = rename_invoice_or_report_contract(doc_type, file, extension)
    elif rename == "delete":
        sure = str(input("Are you sure? [yes/no] ")).lower()
        while sure not in ["yes", "y", "no", "n"]:
            sure = str(input("Are you sure? [yes/no] ")).lower()
        if sure == "yes" or sure == "y":
            os.remove(file)
    elif rename == "exit":
        return False
    return True


def rename_files(dir_path):
    print_header("Starting rename files...")
    for file in dir_walker(dir_path):
        file_name = os.path.basename(file)
        if invoice_validator(file_name) or article_validator(file_name):
            continue
        extension = os.path.splitext(file_name)[1]
        print_info(f"Renaming file: {file_name}")
        process = subprocess.Popen(
            ["xdg-open", file], stdout=subprocess.PIPE, preexec_fn=os.setsid
        )
        intent = get_intent(file, extension)
        if not intent:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            print_info("Exiting...")
            break
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        print_success("File renamed successfully!")
    print_success("Finished renaming files!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python rename_files.py <dir> <new_name>")
        sys.exit(1)
    rename_files(sys.argv[1])
