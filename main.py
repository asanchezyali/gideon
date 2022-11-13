import typer
from remove_duplicate_files import remove_duplicate_files
from rename_files import rename_files


app = typer.Typer()


@app.command()
def duplicates(dir_path: str, autodelete: bool = False):
    remove_duplicate_files(dir_path, autodelete)


@app.command()
def rename(dir_path: str):
    rename_files(dir_path)


if __name__ == "__main__":
    app()
