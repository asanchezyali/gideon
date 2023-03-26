import typer
from src.remove_duplicate_files import remove_duplicate_files
from src.rename_files import rename_files
from src.organize_files import organize_files

app = typer.Typer()


@app.command()
def duplicates(dir_path: str = "/home/alejandrosy/Downloads", autodelete: bool = False):
    """
    Finds duplicate files in a given directory and optionally deletes them.

    Args:
        dir_path (str): The path to the directory to search for duplicates in.
        autodelete (bool): Whether to automatically delete the duplicate files.
            Defaults to False.
    """
    try:
        remove_duplicate_files(dir_path, autodelete)
    except Exception as e:
        typer.echo("An error occurred: ", e)


@app.command()
def rename(dir_path: str = "/home/alejandrosy/Downloads"):
    """
    Renames files in a given directory based on their file extension.

    Args:
        dir_path (str): The path to the directory to rename files in.
    """
    try:
        rename_files(dir_path)
    except Exception as e:
        typer.echo("An error occurred: ", e)


@app.command()
def organize(dir_input: str = "/home/alejandrosy/Downloads", dir_output: str = "/run/media/alejandrosy/Own/Documentos/Own"):
    """
    Organizes files in a given directory into subdirectories based on their file
    extension.

    Args:
        dir_input (str): The path to the directory to organize.
        dir_output (str): The path to the directory to output the organized files
    """
    try:
        organize_files(dir_input, dir_output)
    except Exception as e:
        typer.echo("An error occurred: ", e)


if __name__ == "__main__":
    app()
