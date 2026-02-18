"""Generated entrypoint for project."""

from .services import execute


def run() -> int:
    """Run workflow for folder-hygiene-agent."""
    result = execute({'items': 1})
    return 0 if result.status == 'ok' else 1
