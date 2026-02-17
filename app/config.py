"""Configuration for AutoDev Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AgentConfig:
    """Global configuration values for orchestrator modules."""

    memory_db_path: Path = Path("state/memory.db")
    workspace_root: Path = Path("generated_projects")
    min_complexity: int = 1
    max_complexity: int = 5
    max_files: int = 12
    max_lines_per_file: int = 250
    max_retries: int = 3
    min_test_coverage: int = 85
    run_lint: bool = True
    run_type_check: bool = False
    run_coverage: bool = True
    strict_validation: bool = True
    schedule_lock_file: Path = Path("state/scheduler.lock")
    lock_stale_seconds: int = 3600

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Build config from environment variables with sensible defaults."""
        return cls(
            min_complexity=int(os.getenv("AUTODEV_MIN_COMPLEXITY", "1")),
            max_complexity=int(os.getenv("AUTODEV_MAX_COMPLEXITY", "5")),
            max_retries=int(os.getenv("AUTODEV_MAX_RETRIES", "3")),
            min_test_coverage=int(os.getenv("AUTODEV_MIN_COVERAGE", "85")),
            run_lint=os.getenv("AUTODEV_RUN_LINT", "true").lower() == "true",
            run_type_check=os.getenv("AUTODEV_RUN_TYPECHECK", "false").lower() == "true",
            run_coverage=os.getenv("AUTODEV_RUN_COVERAGE", "true").lower() == "true",
            strict_validation=os.getenv("AUTODEV_STRICT_VALIDATION", "true").lower() == "true",
            lock_stale_seconds=int(os.getenv("AUTODEV_LOCK_STALE_SECONDS", "3600")),
        )

    def ensure_dirs(self) -> None:
        """Create required directories if they do not exist."""
        self.memory_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.schedule_lock_file.parent.mkdir(parents=True, exist_ok=True)
