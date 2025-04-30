import os
import signal
import subprocess
import platform
from pathlib import Path

from gideon.validators import validate_author
from gideon.validators import validate_year
from gideon.validators import validate_title
from gideon.validators import validate_date
from gideon.validators import validate_month
from gideon.validators import validate_day
from gideon.validators import validate_company
from gideon.validators import validate_name
from gideon.validators import validators
from gideon.constants import DocType, TOPICS, EXCLUDE_PROJECT_DIR
from gideon.dir_walker import DirWalker
from gideon.utils.bcolors import print_info, print_header, print_success
from gideon.utils.managers import open_file, close_file


def add_author_to_filename():
    author = str(input("Author: "))
    while not validate_author(author):
        author = str(input("Author: "))
    return author.replace(" ", "_")


def add_year_to_filename():
    year = str(input("Year (YYYY): "))
    while not validate_year(year):
        year = str(input("Year: "))
    return year

def add_month_to_filename():
    month = str(input("Month (MM): "))
    while not validate_month(month):
        month = str(input("Month: "))
    return month

def add_day_to_filename():
    day = str(input("Day (DD): "))
    while not validate_day(day):
        day = str(input("Day: "))
    return day


def add_date_to_filename():
    year = add_year_to_filename()
    month = add_month_to_filename()
    day = add_day_to_filename()
    date = f"{year}_{month}_{day}"
    while not validate_date(date):
        year = add_year_to_filename()
        month = add_month_to_filename()
        day = add_day_to_filename()
        date = f"{year}_{month}_{day}"
    return date

def add_company_name_to_filename():
    company_name = str(input("Company name: "))
    company_name = company_name.upper()
    while not validate_company(company_name):
        company_name = str(input("Company name: "))
    return company_name.replace(" ", "_")


def add_title_to_filename():
    title = str(input("Title: "))
    while not validate_title(title):
        title = str(input("Title: "))
    return title.replace(" ", "_")

def add_name_to_filename():
    name = str(input("Name: "))
    while not validate_name(name):
        name = str(input("Name: "))
    return name.replace(" ", "_")

def add_topic_to_filename():
    print_header("Adding an existing topic to a filename:")
    topics = list(TOPICS.keys())
    topics_length = len(TOPICS.keys())
    for i in range(topics_length):
        print_info(f"{i + 1}. {TOPICS[topics[i]]}")
    option = int(input("Option: "))
    while option not in range(1, topics_length + 1):
        option = int(input("Option: "))
    return topics[option - 1]


def get_user_consent_and_rename(file, new_filename):
    agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()
    while agree not in ["yes", "no"]:
        agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()

    if agree == "yes":
        source = Path(file)
        os.rename(file, source.parent / new_filename)
        return True

    return False


def rename_doc(doc_type, file, extension):
    author = add_author_to_filename()
    year = add_year_to_filename()
    title = add_title_to_filename()
    topic = add_topic_to_filename()
    new_filename = f"{author}.{year}.{title}.{topic}.{doc_type}{extension}"
    return get_user_consent_and_rename(file, new_filename)


def rename_commercial_doc(doc_type, file, extension):
    date = add_date_to_filename()
    company = add_company_name_to_filename()
    name = add_name_to_filename()
    new_filename = f"{date}.{company}.{name}.{doc_type}{extension}"
    return get_user_consent_and_rename(file, new_filename)


def rename_article(file, extension):
    return rename_doc(DocType.ARTICLE, file, extension)


def rename_book(file, extension):
    return rename_doc(DocType.BOOK, file, extension)


def rename_thesis(file, extension):
    return rename_doc(DocType.THESIS, file, extension)

def rename_commercial_document(file, extension):
    return rename_commercial_doc(DocType.COMMERCIAL_DOCUMENT, file, extension)

def rename_legal_document(file, extension):
    return rename_commercial_doc(DocType.LEGAL_DOCUMENT, file, extension)

def rename_nda(file, extension):
    return rename_commercial_doc(DocType.NON_DISCLOSURE_AGREEMENT, file, extension)

def rename_personal_document(file, extension):
    return rename_commercial_doc(DocType.PERSONAL_DOCUMENT, file, extension)

actions = {
    DocType.ARTICLE: rename_article,
    DocType.BOOK: rename_book,
    DocType.THESIS: rename_thesis,
    DocType.COMMERCIAL_DOCUMENT: rename_commercial_document,
    DocType.LEGAL_DOCUMENT: rename_legal_document,
    DocType.NON_DISCLOSURE_AGREEMENT: rename_nda,
    DocType.PERSONAL_DOCUMENT: rename_personal_document,
}


def validate_filename(filename):
    print_header(f"Validating filename: {filename}")
    for doc_type in DocType.get_type_ext_docs():
        if "." + doc_type + "." in filename:
            validated = validators[doc_type](filename)
            return validated
    return False


def get_filename(file):
    return os.path.basename(file)


def set_filename(option, file, filename):
    return actions[DocType.get_type_ext_docs()[option - 1]](
        file, get_extension(filename)
    )


def get_extension(filename):
    return os.path.splitext(filename)[1]


def show_options(filename):
    print_header(f"Select an document type for {filename}:")
    for i in range(DocType.total_types()):
        print_info(f"{i + 1}. {DocType.get_type_docs()[DocType.get_type_ext_docs()[i]]}")
    print_info(f"{DocType.total_types()+1}. Delete file")
    print_info(f"{DocType.total_types()+2}. Exit")


def delete_file(file):
    sure = str(input("Are you sure? [yes/no] ")).lower()
    while sure not in ["yes", "y", "no", "n"]:
        sure = str(input("Are you sure? [yes/no] ")).lower()
    if sure == "yes" or sure == "y":
        os.remove(file)


def change_spaces_with_underscores(dir_path):
    print_header("Starting change spaces with underscores...")
    walker = DirWalker(dir_excludes=EXCLUDE_PROJECT_DIR)
    for file in walker.process_directory(dir_path):
        directory = os.path.dirname(file)
        filename = os.path.basename(file)
        new_filename = filename.replace(" ", "_")
        new_file = os.path.join(directory, new_filename)
        os.rename(file, new_file)
    print_success("Finished changing spaces with underscores!")


def rename_all_files(dir_path):
    print_header("Starting rename files...")
    walker = DirWalker(dir_excludes=EXCLUDE_PROJECT_DIR)
    for file in walker.process_directory(dir_path):
        filename = get_filename(file)
        if validate_filename(filename):
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


def rename_file(file_path: str, doc_type: str) -> bool:
    """
    Rename a file based on its document type.
    
    Args:
        file_path: Path to the file to rename
        doc_type: Document type to use for renaming
        
    Returns:
        bool: True if file was renamed successfully, False otherwise
    """
    extension = get_extension(file_path)
    if doc_type in actions:
        return actions[doc_type](file_path, extension)
    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python rename_files.py <dir> <new_name>")
        sys.exit(1)
    rename_all_files(sys.argv[1])
