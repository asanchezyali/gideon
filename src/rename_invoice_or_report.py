import os
from pathlib import Path
from src.filename_formats import validate_date
from src.filename_formats import validate_company_name

def rename_invoice_or_report_contract(doc_type, file, extension):
    date = str(input("Date: "))
    while not validate_date(date):
        date = str(input("Date: "))
    company = str(input("Company: ")).upper()
    while not validate_company_name(company):
        company = str(input("Company: ")).upper()
    new_filename = f"{date}.{company}.{doc_type}{extension}"
    agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()
    while agree not in ["yes", "no"]:
        agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()
    if agree == "yes":
        # Put new filename in the same directory as the old filename
        source = Path(file)
        os.rename(file, source.parent / new_filename)
        return True
    return False