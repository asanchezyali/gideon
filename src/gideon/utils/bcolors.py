from rich.console import Console

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
    console.print(f"{BColors.GREEN}{message}{BColors.GREEN}")


def print_error(message: str) -> None:
    console.print(f"{BColors.RED}{message}{BColors.RED}")


def print_warning(message: str) -> None:
    console.print(f"{BColors.YELLOW}{message}{BColors.YELLOW}")


def print_info(message: str) -> None:
    console.print(f"{BColors.BLUE}{message}{BColors.BLUE}")


def print_debug(message: str) -> None:
    console.print(f"{BColors.WHITE}{message}{BColors.WHITE}")
