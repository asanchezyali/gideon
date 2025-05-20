import typer
from .commands.rename import rename_app

app = typer.Typer(
    help="Gideon CLI - AI-powered Personal Assistant",
    no_args_is_help=True,
)

# Register commands
app.add_typer(rename_app, name="rename", help="Rename files using AI analysis")

if __name__ == "__main__":
    app() 