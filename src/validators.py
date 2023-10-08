from utils.bcolors import print_info, print_error
from src.constants import MONTHS, TOPICS, DocType, FORMAT_NORMAL_DOC, FORMAT_COMMERCIAL_DOC


def validate_title(title):
    if len(title.split(" ")) > 10:
        print_error(f"{title} is not a valid title")
        print_info(f"Expected format: at least 10 words for title")
        return False
    return True


def validate_company(company):
    if len(company.split(" ")) > 4:
        print_error(f"{company} is not a valid company name")
        print_info(f"Expected format: at least 4 words for company name")
        return False
    return True


def validate_name(name):
    if len(name.split(" ")) > 4:
        print_error(f"{name} is not a valid name")
        print_info(f"Expected format: at least 4 words for name")
        return False
    return True


def validate_year(year):
    if len(year) != 4:
        print_error(f"{year} is not a valid year")
        return False
    return True


def validate_month(month):
    if month not in MONTHS:
        print_error(f"{month} is not a valid month")
        print_info(f"Expected format: {MONTHS}")
        return False
    return True


def validate_day(day):
    if len(day) != 2:
        print_error(f"{day} is not a valid day")
        return False
    return True


def validate_author(author):
    if len(author.split(" ")) > 4:
        print_error(f"{author} is not a valid author")
        print_info(f"Expected format: at least 4 words for author")
        return False

    if "." in author:
        print_error(f"{author} is not a valid author")
        print_info(f"Expected format: no points in author")
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


def validate_topic(topic):
    if topic not in TOPICS:
        print_error(f"{topic} is not a valid topic")
        print_info(f"Expected format: {TOPICS}")
        return False
    return True


def validate_doc_type(doc_type):
    if doc_type not in DocType.get_type_ext_docs():
        print_error(f"{doc_type} is not a valid document type")
        print_info(f"Expected format: {DocType.get_type_ext_docs()}")
        return False
    return True


def validate_doc_name_length(chunks, doc_name):
    if len(chunks) != 6:
        print_error(f"{doc_name} is not a valid document name")
        print_info(f"Expected format: {FORMAT_NORMAL_DOC}")
        return False
    return True


def validate_doc(filename):
    chunks = filename.split(".")
    validated_doc_name_length = validate_doc_name_length(chunks, filename)
    if not validated_doc_name_length:
        return False
    author, year, title, topic, doc_type, extension = chunks
    validated_author = validate_author(author)
    if not validated_author:
        return False
    validated_year = validate_year(year)
    if not validated_year:
        return False
    validated_title = validate_title(title)
    if not validated_title:
        return False
    validated_topic = validate_topic(topic)
    if not validated_topic:
        return False
    validated_doc_type = validate_doc_type(doc_type)
    if not validated_doc_type:
        return False
    return (
        validated_doc_name_length
        and validated_author
        and validated_year
        and validated_title
        and validated_topic
        and validated_doc_type
    )


def validate_article(filename):
    return validate_doc(filename)


def validate_book(filename):
    return validate_doc(filename)


def validate_thesis(filename):
    return validate_doc(filename)


def validate_commercial_doc_name_length(chunks, doc_name):
    if len(chunks) != 5:
        print_error(f"{doc_name} is not a valid document name")
        print_info(f"Expected format: {FORMAT_COMMERCIAL_DOC}")
        return False
    return True


def validate_commercial_doc(filename):
    chunks = filename.split(".")
    validated_doc_name_length = validate_commercial_doc_name_length(chunks, filename)
    if not validated_doc_name_length:
        return False
    date, company, name, doc_type, extension = chunks
    validated_date = validate_date(date)
    if not validated_date:
        return False
    validated_company = validate_company(company)
    if not validated_company:
        return False
    validated_name = validate_name(name)
    if not validated_name:
        return False
    validated_doc_type = validate_doc_type(doc_type)
    if not validated_doc_type:
        return False
    return (
        validated_doc_name_length
        and validated_date
        and validated_company
        and validated_name
        and validated_doc_type
    )


def validate_commercial_document(filename):
    return validate_commercial_doc(filename)


def validate_legal_document(filename):
    return validate_commercial_doc(filename)


def validate_nda(filename):
    return validate_commercial_doc(filename)

def validate_personal_document(filename):
    return validate_commercial_doc(filename)


validators = {
    DocType.ARTICLE: validate_article,
    DocType.BOOK: validate_book,
    DocType.THESIS: validate_thesis,
    DocType.COMMERCIAL_DOCUMENT: validate_commercial_document,
    DocType.LEGAL_DOCUMENT: validate_legal_document,
    DocType.NON_DISCLOSURE_AGREEMENT: validate_nda,
    DocType.PERSONAL_DOCUMENT: validate_personal_document,
}

def validate_project_name(project_name_dir):
    print_info(f"Opening {project_name_dir}")
    if len(project_name_dir.split("_")) == 3:
        return True
    return False