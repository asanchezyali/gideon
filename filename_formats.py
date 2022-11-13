from bcolors import bcolors, print_warning, print_error

invoice = "%Y_%m_%d.CompanyName.invoice.pdf"
article_or_book = "AuthorName.Year.Title.topic.article_or_book.pdf"

MONTHS = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]

COMPANY_NAMES = [
    "TIGO",
    "EPM",
    "BANCOLOMBIA",
    "BCSC",
    "MONADICAL",
    "DAVIVIENDA",
]


def invoice_validator(filename):
    chunks = filename.split(".")
    if len(chunks) != 4:
        print_error(f"{filename} is not a valid invoice filename")
        print_warning(f"Expected format: {invoice}")
        return False
    date, company, _, extension = chunks
    if not validate_date(date):
        print_error(f"{date} is not a valid date")
        print_warning(f"Expected format: %Y_%m_%d")
        return False
    if company not in COMPANY_NAMES:
        print_error(f"{company} is not a valid company name")
        print_warning(f"Expected format: {COMPANY_NAMES}")
        return False
    if extension != "pdf":
        print_error(f"{filename} extension is not pdf")
        return False


def validate_date(date):
    chunks = date.split("_")
    if len(chunks) != 3:
        print_error(f"{date} is not a valid date")
        return False
    year, month, day = chunks
    if len(year) != 4:
        print_error(f"{year} is not a valid year")
        return False
    if len(month) not in MONTHS:
        print_error(f"{month} is not a valid month")
        print_warning(f"Expected format: {MONTHS}")
        return False
    if len(day) != 2:
        print_error(f"{day} is not a valid day")
        return False
    return True
