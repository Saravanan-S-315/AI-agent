"""Domain models for AutoDev Agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProjectCategory(str, Enum):
    """Supported project categories."""

    CLI = "cli_utilities"
    API = "rest_apis"
    DATA = "data_processing"
    AUTOMATION = "automation_scripts"
    AI = "ai_utilities"


@dataclass(slots=True)
class ProjectIdea:
    """A generated project concept."""

    name: str
    category: ProjectCategory
    complexity: int
    summary: str


@dataclass(slots=True)
class PlanArtifact:
    """Architecture plan generated before code creation."""

    structure: list[str]
    dependencies: list[str]
    interfaces: list[str]
    test_outline: list[str]


@dataclass(slots=True)
class ValidationResult:
    """Result of local validation checks."""

    success: bool
    checks: dict[str, bool] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RunRecord:
    """Execution log entry for a single run."""

    started_at: datetime
    finished_at: datetime
    project_name: str
    retries: int
    success: bool
