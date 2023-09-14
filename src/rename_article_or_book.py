import os
from pathlib import Path
from src.filename_formats import validate_author
from src.filename_formats import validate_year
from src.filename_formats import validate_title
from src.constants import DocType, TOPICS
from utils.bcolors import print_header

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
        print(f"{i + 1}. {TOPICS[topics[i]]}")
    option = int(input("Option: "))
    while option not in range(1, topics_length + 1):
        option = int(input("Option: "))
    return topics[option - 1]

def rename_file(doc_type, file, extension):
    author = add_author_to_filename()
    year = add_year_to_filename()
    title = add_title_to_filename()
    topic = add_topic_to_filename()
    
    new_filename = f"{author}.{year}.{title}.{topic}.{doc_type}{extension}"
    
    agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()
    while agree not in ["yes", "no"]:
        agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()

    if agree == "yes":
        source = Path(file)
        os.rename(file, source.parent / new_filename)
        return True
        
    return False

def rename_article(file, extension):
    return rename_file(DocType.ARTICLE, file, extension)

def rename_book(file, extension):
    return rename_file(DocType.BOOK, file, extension)

def rename_thesis(file, extension):
    return rename_file(DocType.THESIS, file, extension)



