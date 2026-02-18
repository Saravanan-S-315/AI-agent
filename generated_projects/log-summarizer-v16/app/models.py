"""Generated domain models."""

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionResult:
    status: str
    processed_items: int
