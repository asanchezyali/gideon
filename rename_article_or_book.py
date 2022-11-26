import os
from filename_formats import validate_author
from filename_formats import validate_year
from filename_formats import validate_title
from filename_formats import validate_topic
from filename_formats import validate_article_or_book


def rename_article_or_book(dir_path, file, extension):
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
    article_or_book = str(input("Article or book? [article/book] ")).lower()
    while not validate_article_or_book(article_or_book):
        article_or_book = str(input("Article or book? [article/book] ")).lower()
    new_filename = f"{author}.{year}.{title}.{topic}.{article_or_book}.{extension}"
    agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()
    while agree not in ["yes", "no"]:
        agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()
    if agree == "yes":
        os.rename(file, os.path.join(dir_path, new_filename))
        return True
    return False



