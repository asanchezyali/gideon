from bcolors import print_warning, print_error

invoice_or_report = "%Y_%m_%d.CompanyName.invoice_or_report.pdf"
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


TOPICS = [
    "math",
    "topology",
    "algebra",
    "geometry",
    "analysis",
    "number_theory",
    "combinatorics",
    "logic",
    "set_theory",
    "probability",
    "graph_theory",
    "linear_algebra",
    "complex_analysis",
    "differential_equations",
    "statistics",
    "functional_analysis",
    "numerical_analysis",
    "algorithms",
    "machine_learning",
    "artificial_intelligence",
    "deep_learning",
    "data_science",
    "physics",
    "chemistry",
    "biology",
    "computer_science",
    "economics",
    "finance",
    "statistics",
    "psychology",
    "sociology",
    "philosophy",
    "history",
    "geography",
    "politics",
    "law",
    "engineering",
    "medicine",
    "architecture",
    "art",
    "music",
    "theater",
    "dance",
    "literature",
    "religion",
    "other",
]

def invoice_validator(filename):
    chunks = filename.split(".")
    if len(chunks) != 4:
        print_error(f"{filename} is not a valid invoice filename")
        print_warning(f"Expected format: {invoice_or_report}")
        return False
    date, company, invoice_or_report, extension = chunks
    if not validate_date(date):
        print_error(f"{date} is not a valid date")
        print_warning(f"Expected format: %Y_%m_%d")
        return False
    if company not in COMPANY_NAMES:
        print_error(f"{company} is not a valid company name")
        print_warning(f"Expected format: {COMPANY_NAMES}")
        return False
    if invoice_or_report not in ["invoice", "report"]:
        print_error(f"{invoice_or_report} is not a valid invoice or report")
        print_warning(f"Expected format: invoice or report")
        return False
    if extension != "pdf":
        print_error(f"{filename} extension is not pdf")
        return False

def article_validator(filename):
    chunks = filename.split(".")
    if len(chunks) != 5:
        print_error(f"{filename} is not a valid article filename")
        print_warning(f"Expected format: {article_or_book}")
        return False
    author, year, title, topic, extension = chunks
    if not validate_author(author):
        print_error(f"{author} is not a valid author")
        return False
    if not validate_year(year):
        print_error(f"{year} is not a valid year")
        return False
    if not validate_title(title):
        print_error(f"{title} is not a valid title")
        return False
    if not validate_topic(topic):
        print_error(f"{topic} is not a valid topic")
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

def validate_author(author):
    if len(author) < 3:
        print_error(f"{author} is not a valid author")
        print_warning(f"Expected format: at least 3 characters")
        return False
    return True

def validate_year(year):
    if len(year) != 4:
        print_error(f"{year} is not a valid year")
        return False
    return True

def validate_title(title):
    if len(title) < 10:
        print_error(f"{title} is not a valid title")
        print_warning(f"Expected format: at least 10 characters")
        return False
    return True

def validate_topic(topic):
    if topic not in TOPICS:
        print_error(f"{topic} is not a valid topic")
        print_warning(f"Expected format: {TOPICS}")
        return False
    return True

def validator_filename(filename):
    if filename.endswith(".pdf"):
        if filename.startswith("20"):
            return invoice_validator(filename)
        else:
            return article_validator(filename)
    else:
        print_error(f"{filename} is not a pdf file")
        return False