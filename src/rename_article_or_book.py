import os
from pathlib import Path
from src.validators import validate_author
from src.validators import validate_year
from src.validators import validate_title
from src.validators import validate_date
from src.constants import DocType, TOPICS
from utils.bcolors import print_header, print_info


def add_author_to_filename():
    author = str(input("Author: "))
    while not validate_author(author):
        author = str(input("Author: "))
    return author


def add_year_to_filename():
    year = str(input("Year (YYYY): "))
    while not validate_year(year):
        year = str(input("Year: "))
    return year


def add_date_to_filename():
    date = str(input("Date (YYYY_MM_DD): "))
    while not validate_date(date):
        date = str(input("Date: "))
    return date


def add_company_name_to_filename():
    company_name = str(input("Company name: "))
    return company_name


def add_title_to_filename():
    title = str(input("Title: "))
    while not validate_title(title):
        title = str(input("Title: "))
    return title


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


def rename_file(doc_type, file, extension):
    author = add_author_to_filename()
    year = add_year_to_filename()
    title = add_title_to_filename()
    topic = add_topic_to_filename()

    new_filename = f"{author}.{year}.{title}.{topic}.{doc_type}{extension}"

    return get_user_consent_and_rename(file, new_filename)


def rename_commercial_doc(doc_type, file, extension):
    company = add_company_name_to_filename()
    date = add_date_to_filename()

    new_filename = f"{company}.{date}.{doc_type}{extension}"

    return get_user_consent_and_rename(file, new_filename)


def rename_article(file, extension):
    return rename_file(DocType.ARTICLE, file, extension)


def rename_book(file, extension):
    return rename_file(DocType.BOOK, file, extension)


def rename_thesis(file, extension):
    return rename_file(DocType.THESIS, file, extension)

def rename_commercial_document(file, extension):
    return rename_commercial_doc(DocType.COMMERCIAL_DOCUMENT, file, extension)

def rename_legal_document(file, extension):
    return rename_commercial_doc(DocType.LEGAL_DOCUMENT, file, extension)

def rename_nda(file, extension):
    return rename_commercial_doc(DocType.NON_DISCLOSURE_AGREEMENT, file, extension)
