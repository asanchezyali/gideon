"""Logging utilities for the Gideon application."""
import threading
from typing import Optional
from rich.console import Console

# Global console instance
_console = Console()
# Lock to prevent concurrent writes to console
_console_lock = threading.Lock()

# Flag to disable standard output (for example during progress bars)
_quiet_mode = False
# Store messages to display later when quiet mode is disabled
_message_queue = []


def set_quiet_mode(quiet: bool):
    """Set the quiet mode to prevent console output."""
    global _quiet_mode
    _quiet_mode = quiet


def flush_messages():
    """Display all queued messages."""
    global _message_queue
    if _message_queue:
        with _console_lock:
            for style, message in _message_queue:
                _console.print(message, style=style)
        _message_queue.clear()


def log_message(message: str, style: Optional[str] = None):
    """Log a message to the console or queue it if in quiet mode."""
    global _message_queue, _quiet_mode
    if _quiet_mode:
        _message_queue.append((style, message))
    else:
        with _console_lock:
            _console.print(message, style=style)


def log_info(message: str):
    """Log an informational message."""
    log_message(message, style="yellow")


def log_error(message: str):
    """Log an error message."""
    log_message(message, style="red")


def log_success(message: str):
    """Log a success message."""
    log_message(message, style="green")

def log_warning(message: str):
    """Log a warning message."""
    log_message(message, style="magenta")
