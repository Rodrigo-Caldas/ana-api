"""Utilitário para logging, traceback e terminal em geral."""

import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

install(show_locals=True)

console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True, console=console)],
    force=True,
)

# ou __name__, caso o esquema de logging não seja destinado a funções lambda
log = logging.getLogger("__name__")
logging.getLogger("httpx").setLevel(logging.ERROR)
