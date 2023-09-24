import typer
import os

from src.duplicate_files import remove_duplicate_files
from src.rename_files import rename_all_files, change_spaces_with_underscores
from src.organize_files import organize_files

app = typer.Typer()
os.chdir("..")
non_categorized_info = os.path.join(os.getcwd(), "NonCategorizedInfo")
categorized_info = os.path.join(os.getcwd(), "CategorizedInfo")


@app.command()
def remove_duplicates(auto_delete: bool = False):
    """
    Finds duplicate files in a given directory and optionally deletes them.

    Args:
        dir_path (str): The path to the directory to search for duplicates in.
        autodelete (bool): Whether to automatically delete the duplicate files.
            Defaults to False.
    """

    try:
        remove_duplicate_files(non_categorized_info, auto_delete)
    except Exception as e:
        typer.echo("An error occurred: ", e)


@app.command()
def rename():
    """
    Renames files in a given directory based on their file extension.

    Args:
        dir_path (str): The path to the directory to rename files in.
    """
    try:
        rename_all_files(non_categorized_info)
    except Exception as e:
        typer.echo("An error occurred: ", e)


@app.command()
def change_spaces():
    """
    Changes spaces in filenames to underscores in a given directory.

    Args:
        dir_path (str): The path to the directory to rename files in.
    """
    try:
        change_spaces_with_underscores(non_categorized_info)
    except Exception as e:
        typer.echo("An error occurred: ", e)


@app.command()
def organize():
    """
    Organizes files in a given directory into subdirectories based on their file
    extension.

    Args:
        dir_input (str): The path to the directory to organize.
        dir_output (str): The path to the directory to output the organized files
    """
    try:
        organize_files(non_categorized_info, categorized_info)
    except Exception as e:
        typer.echo("An error occurred: ", e)


if __name__ == "__main__":
    app()
