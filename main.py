import typer
from remove_duplicate_files import remove_duplicate_files


app = typer.Typer()


@app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")


@app.command()
def duplicates(dir_path: str, autodelete: bool = False):
    remove_duplicate_files(dir_path, autodelete)
    typer.echo(f"Duplicate files removed from {dir_path}")

if __name__ == "__main__":
    app()
