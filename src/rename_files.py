import os
import signal
import subprocess
from src.dir_walker import dir_walker
from utils.bcolors import print_info, print_header, print_success
from src.rename_article_or_book import rename_article_or_book
from src.rename_invoice_or_report import rename_invoice_or_report
from src.filename_formats import invoice_validator, article_validator


def get_intent(dir_path, file, extension):
    rename = str(input("Rename? [yes/no/delete/exit] ")).lower()
    while rename not in ["yes", "y", "no", "n", "delete", "exit"]:
        rename = str(input("Rename? [yes/no/delete/exit] ")).lower()
    if rename == "yes" or rename == "y":
        doc_type = str(
            input(
                "Article or book or invoice or report? [article/book/invoice/report] "
            )
        ).lower()
        while doc_type not in ["article", "book", "invoice", "report"]:
            doc_type = str(
                input(
                    "Article or book or invoice or report? [article/book/invoice/report] "
                )
            ).lower()
        if doc_type == "article" or doc_type == "book":
            renamed = rename_article_or_book(doc_type, file, extension)
            while not renamed:
                renamed = rename_article_or_book(doc_type, file, extension)
        elif doc_type == "invoice" or doc_type == "report":
            renamed = rename_invoice_or_report(doc_type, file, extension)
            while not renamed:
                renamed = rename_invoice_or_report(doc_type, file, extension)
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
        intent = get_intent(dir_path, file, extension)
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
