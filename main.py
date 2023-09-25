import typer
import os

from src.delete_duplicated_files import remove_duplicate_files
from src.rename_files import rename_all_files, change_spaces_with_underscores
from src.organize_files import organize_all_files, _delete_empty_dirs, move_project_dir

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
def rename_files():
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
def remove_name_spaces():
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
def organize_files():
    """
    Organizes files in a given directory into subdirectories based on their file
    extension.

    Args:
        dir_input (str): The path to the directory to organize.
        dir_output (str): The path to the directory to output the organized files
    """
    try:
        organize_all_files(non_categorized_info, categorized_info)
    except Exception as e:
        typer.echo("An error occurred: ", e)


@app.command()
def recalculate_hashes():
    """
    Recalculates the hashes of all files in a given directory.

    Args:
        dir_path (str): The path to the directory to recalculate hashes in.
    """
    pass


@app.command()
def delete_empty_dirs():
    """
    Deletes all empty directories in a given directory.

    Args:
        dir_path (str): The path to the directory to delete empty directories in.
    """
    try:
        _delete_empty_dirs(non_categorized_info)
    except Exception as e:
        typer.echo("An error occurred: ", e)


@app.command()
def organize_projects():
    """
    Organizes projects in a given directory into subdirectories based on their
    project type.

    Args:
        dir_input (str): The path to the directory to organize.
        dir_output (str): The path to the directory to output the organized files
    """
    try:
        move_project_dir(non_categorized_info, categorized_info)
    except Exception as e:
        typer.echo("An error occurred: ", e)


if __name__ == "__main__":
    app()
