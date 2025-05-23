import typer
from .commands.rename import rename_app
from .commands.remove_duplicates import remove_duplicates_app

app = typer.Typer(
    help="Gideon CLI - AI-powered Personal Assistant",
    no_args_is_help=True,
)

# Register commands
app.add_typer(rename_app, name="rename", help="Rename files using AI analysis")
# Remove duplicate files
app.add_typer(remove_duplicates_app, name="remove-duplicates", help="Remove duplicate files")
if __name__ == "__main__":
    app()
