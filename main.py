import typer
from src.remove_duplicate_files import remove_duplicate_files
from src.rename_files import rename_files
from src.organize_files import organize_files

app = typer.Typer()


@app.command()
def duplicates(dir_path: str, autodelete: bool = False):
    remove_duplicate_files(dir_path, autodelete)


@app.command()
def rename(dir_path: str):
    rename_files(dir_path)

@app.command()
def organize(dir_input: str, dir_output: str):
    organize_files(dir_input, dir_output)


if __name__ == "__main__":
    app()
