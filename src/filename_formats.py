from utils.bcolors import print_info, print_error

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
    "A2CENSO",
    "ARUS",
    "ARUS_BCSC",
    "ARUS_BANCOLOMBIA",
    "EPM_BCSC",
    "EPM_BANCOLOMBIA",
    "A2CENSO_BCSC",
    "A2CENSOS_BANCOLOMBIA",
    "DAVIVIENDA_BCSC",
    "DAVIVIENDA_BANCOLOMBIA",
    "CONSTRUCASAS",
    "CONSTRUCASAS_BCSC",
    "CONSTRUCASAS_BANCOLOMBIA",
    "SIIGO",
    "DIAN",
    "SURAMERICANA",
    "ACCIONESYVALORES",
]


TOPICS = [
    "mathematics",
    "topology_geometry",
    "algebra_number_theory",
    "analysis",
    "set_theory_logic",
    "probability_statistics",
    "computer_science",
    "machine_learning_AI",
    "physical_sciences",
    "biological_sciences",
    "social_sciences",
    "economics_finance",
    "psychology_sociology",
    "humanities",
    "arts",
    "engineering",
    "business",
    "health",
    "blockchain",
    "other",
]



def invoice_validator(filename):
    try:
        chunks = filename.split(".")
        if len(chunks) != 4:
            print_error(f"{filename} is not a valid invoice filename")
            print_info(f"Expected format: {invoice_or_report}")
            return False
        date, company, invoice_or_report, extension = chunks
        if not validate_date(date):
            print_error(f"{date} is not a valid date")
            print_info(f"Expected format: %Y_%m_%d")
            return False
        if not validate_company_name(company):
            print_error(f"{company} is not a valid company name")
            return False
        if not validate_invoice_or_report_contract(invoice_or_report):
            print_error(f"{invoice_or_report} is not a valid invoice or report")
            return False
        if extension != "pdf":
            print_error(f"{filename} extension is not pdf")
            return False
        return True
    except Exception as e:
        print_error(f"{filename} is not a valid invoice filename")
        return False


def article_validator(filename):
    try:
        chunks = filename.split(".")
        if len(chunks) != 6:
            print(chunks)
            print_error(f"{filename} is not a valid article filename")
            print_info(f"Expected format: {article_or_book}")
            return False
        author, year, title, topic, doc_type, extension = chunks
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
        if not validate_article_or_book(doc_type):
            print_error(f"{doc_type} is not a valid type")
            return False
        if extension not in ["pdf", "txt"]:
            print_error(f"{filename} extension is not pdf or txt")
            return False
        return True
    except Exception as e:
        print_error(f"{filename} is not a valid article filename")
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
    if month not in MONTHS:
        print_error(f"{month} is not a valid month")
        print_info(f"Expected format: {MONTHS}")
        return False
    if len(day) != 2:
        print_error(f"{day} is not a valid day")
        return False
    return True


def validate_company_name(company_name):
    if company_name not in COMPANY_NAMES:
        print_error(f"{company_name} is not a valid company name")
        print_info(f"Expected format: {COMPANY_NAMES}")
        return False
    return True


def validate_invoice_or_report_contract(invoice_or_report_contract):
    if invoice_or_report_contract not in ["invoice", "report", "contract"]:
        print_error(f"{invoice_or_report_contract} is not a valid invoice or report")
        print_info(f"Expected format: invoice or report or contract")
        return False
    return True


def validate_author(author):
    if len(author.split(" ")) > 4:
        print_error(f"{author} is not a valid author")
        print_info(f"Expected format: at least 4 words for author")
        return False
    return True


def validate_year(year):
    if len(year) != 4:
        print_error(f"{year} is not a valid year")
        return False
    return True


def validate_title(title):
    if len(title.split(" ")) > 10:
        print_error(f"{title} is not a valid title")
        print_info(f"Expected format: at least 10 words for title")
        return False
    return True


def validate_topic(topic):
    if topic not in TOPICS:
        print_error(f"{topic} is not a valid topic")
        print_info(f"Expected format: {TOPICS}")
        return False
    return True


def validate_article_or_book(doc_type):
    if doc_type not in ["article", "book"]:
        print_error(f"{doc_type} is not a valid type")
        print_info(f"Expected format: article or book")
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
