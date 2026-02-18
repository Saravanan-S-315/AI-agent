"""Generated entrypoint for project."""

from .services import execute


def run() -> int:
    """Run workflow for ci-log-parser-v2."""
    result = execute({'items': 1})
    return 0 if result.status == 'ok' else 1
