import typer
from .commands.rename import rename_app
from .commands.remove_duplicates import remove_duplicates_app
from .commands.organize import organize_app
from .commands.search import search_app
from .commands.deduplicate import deduplicate_app
from .commands.chat import chat_app
from .commands.summarize import app as summarize_app
from .commands.references import app as references_app
from .commands.analytics import app as analytics_app
from .commands.review import app as review_app

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
app.add_typer(summarize_app, name="summarize", help="Generate document summaries")
app.add_typer(references_app, name="references", help="Extract bibliographic references")
app.add_typer(review_app, name="review", help="Generate literature reviews")
app.add_typer(analytics_app, name="analytics", help="Analytics and visualizations")
if __name__ == "__main__":
    app()
