from rich.console import Console
from .logging import log_message

console = Console()


class BColors:
    GREEN = "[green]"
    RED = "[red]"
    YELLOW = "[yellow]"
    BLUE = "[blue]"
    MAGENTA = "[magenta]"
    CYAN = "[cyan]"
    WHITE = "[white]"


def print_success(message: str) -> None:
    log_message(message, style="green")


def print_error(message: str) -> None:
    log_message(message, style="red")


def print_warning(message: str) -> None:
    log_message(message, style="yellow")


def print_info(message: str) -> None:
    log_message(message, style="blue")


def print_debug(message: str) -> None:
    log_message(message, style="white")
