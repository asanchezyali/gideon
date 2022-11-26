import os
from filename_formats import validate_date
from filename_formats import validate_company_name
from filename_formats import validate_invoice_or_report

def rename_invoice_or_report(dir_path, file, extension):
    date = str(input("Date: "))
    while not validate_date(date):
        date = str(input("Date: "))
    company = str(input("Company: ")).lower()
    while not validate_company_name(company):
        company = str(input("Company: ")).lower()
    invoice_or_report = str(input("Invoice or report? [invoice/report] ")).lower()
    while not validate_invoice_or_report(invoice_or_report):
        invoice_or_report = str(input("Invoice or report? [invoice/report] ")).lower()
    new_filename = f"{date}.{company}.{invoice_or_report}.{extension}"
    agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()
    while agree not in ["yes", "no"]:
        agree = str(input(f"Rename {file} to {new_filename}? [yes/no] ")).lower()
    if agree == "yes":
        os.rename(file, os.path.join(dir_path, new_filename))
        return True
    return False