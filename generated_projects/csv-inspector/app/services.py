"""Generated service layer."""

from .models import ExecutionResult


def execute(payload: dict[str, int]) -> ExecutionResult:
    """Execute business logic with input validation."""
    if payload.get('items', 0) < 0:
        raise ValueError('items must be non-negative')
    return ExecutionResult(status='ok', processed_items=payload.get('items', 0))  # noqa: E501
