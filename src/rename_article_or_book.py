import os
from pathlib import Path
from src.filename_formats import validate_author
from src.filename_formats import validate_year
from src.filename_formats import validate_title
from src.filename_formats import validate_topic


def rename_article_or_book(doc_type, file, extension):
    author = str(input("Author: "))
    while not validate_author(author):
        author = str(input("Author: "))
    year = str(input("Year: "))
    while not validate_year(year):
        year = str(input("Year: "))
    title = str(input("Title: "))
    while not validate_title(title):
        title = str(input("Title: "))
    topic = str(input("Topic: ")).lower()
    while not validate_topic(topic):
        topic = str(input("Topic: ")).lower()
    new_filename = f"{author}.{year}.{title}.{topic}.{doc_type}{extension}"
    agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()
    while agree not in ["yes", "no"]:
        agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()
    if agree == "yes":
        source = Path(file)
        os.rename(file, source.parent / new_filename)
        return True
    return False



