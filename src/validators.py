from utils.bcolors import print_info, print_error
from src.constants import MONTHS



def validate_title(title):
    if len(title.split(" ")) > 10:
        print_error(f"{title} is not a valid title")
        print_info(f"Expected format: at least 10 words for title")
        return False
    return True


def validate_year(year):
    if len(year) != 4:
        print_error(f"{year} is not a valid year")
        return False
    return True


def validate_author(author):
    if len(author.split(" ")) > 4:
        print_error(f"{author} is not a valid author")
        print_info(f"Expected format: at least 4 words for author")
        return False
    return True


def validate_date(date):
    chunks = date.split("_")
    if len(chunks) != 3:
        print_error(f"{date} is not a valid date")
        return False
    year, month, day = chunks
    if len(year) != 4:
        print_error(f"{year} is not a valid year")
        return False
    if month not in MONTHS:
        print_error(f"{month} is not a valid month")
        print_info(f"Expected format: {MONTHS}")
        return False
    if len(day) != 2:
        print_error(f"{day} is not a valid day")
        return False
    return True
