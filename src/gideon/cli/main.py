import typer
from .commands.rename import rename_app
from .commands.remove_duplicates import remove_duplicates_app
from .commands.organize import organize_app
from .commands.search import search_app
from .commands.deduplicate import deduplicate_app
from .commands.chat import chat_app

app = typer.Typer(
    help="Gideon CLI - AI-powered Research Assistant",
    no_args_is_help=True,
)

# Register commands
app.add_typer(rename_app, name="rename", help="Rename files using AI analysis")
app.add_typer(remove_duplicates_app, name="remove-duplicates", help="Remove duplicate files (legacy)")
app.add_typer(deduplicate_app, name="deduplicate", help="Smart duplicate detection and removal")
app.add_typer(organize_app, name="organize", help="Organize files into folders based on AI analysis")
app.add_typer(search_app, name="search", help="Semantic search and Q&A over documents")
app.add_typer(chat_app, name="chat", help="Interactive research assistant chat")
if __name__ == "__main__":
    app()
