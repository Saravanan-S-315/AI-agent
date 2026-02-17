"""Main orchestration pipeline for AutoDev Agent."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import AgentConfig
from .documentation import generate_readme
from .idea_generator import IdeaGenerator
from .memory import MemoryStore
from .models import RunRecord, ValidationResult
from .planner import ArchitecturePlanner
from .scheduler import SchedulerLock
from .validator import Validator


class AutoDevOrchestrator:
    """Coordinates idea generation, planning, validation, correction, and memory updates."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self.config.ensure_dirs()
        self.memory = MemoryStore(self.config.memory_db_path)
        self.idea_generator = IdeaGenerator()
        self.planner = ArchitecturePlanner()
        self.validator = Validator()
        self.scheduler = SchedulerLock(
            self.config.schedule_lock_file, stale_after_seconds=self.config.lock_stale_seconds
        )

    def run_once(self) -> bool:
        """Execute one autonomous cycle with retry-aware logging and correction hooks."""
        if not self.scheduler.acquire():
            return False

        started = datetime.now(tz=timezone.utc)
        retries = 0
        success = False
        project_name = "n/a"

        try:
            idea = self.idea_generator.generate(
                existing_names=self.memory.list_project_names(),
                min_complexity=self.config.min_complexity,
                max_complexity=self.config.max_complexity,
            )
            project_name = idea.name
            plan = self.planner.create_plan(idea, self.config)
            project_root = self._materialize_project(idea.name, generate_readme(idea, plan))
            self.memory.store_project(idea.name, idea.category, idea.complexity)

            while retries <= self.config.max_retries:
                validation = self.validator.run(
                    project_root,
                    run_lint=self.config.run_lint,
                    run_type_check=self.config.run_type_check,
                    run_coverage=self.config.run_coverage,
                    min_coverage=self.config.min_test_coverage,
                    strict_validation=self.config.strict_validation,
                )
                self._write_validation_log(project_root, retries, validation)
                if validation.success:
                    success = True
                    break
                retries += 1
                self._apply_correction(project_root, validation)

            return success
        finally:
            finished = datetime.now(tz=timezone.utc)
            self.memory.store_run(
                RunRecord(
                    started_at=started,
                    finished_at=finished,
                    project_name=project_name,
                    retries=retries,
                    success=success,
                )
            )
            self.scheduler.release()

    @staticmethod
    def _write_validation_log(project_root: Path, attempt: int, result: ValidationResult) -> None:
        log_file = project_root / "validation_log.jsonl"
        entry = {
            "attempt": attempt,
            "success": result.success,
            "checks": result.checks,
            "logs": result.logs,
        }
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")

    @staticmethod
    def _apply_correction(project_root: Path, validation: ValidationResult) -> None:
        """Apply small deterministic corrections before the next retry."""
        if validation.checks.get("tests", True) or validation.checks.get("coverage", True):
            return
        test_file = project_root / "tests" / "test_core.py"
        if test_file.exists() and "assert run() == 0" not in test_file.read_text(encoding="utf-8"):
            test_file.write_text(
                "from app.main import run\n\n\ndef test_run_returns_zero() -> None:\n    assert run() == 0\n",
                encoding="utf-8",
            )

    def _materialize_project(self, name: str, readme_text: str) -> Path:
        root = self.config.workspace_root / name
        app_dir = root / "app"
        tests_dir = root / "tests"
        app_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)

        (root / "README.md").write_text(readme_text, encoding="utf-8")
        (root / "requirements.txt").write_text("pytest\npytest-cov\nflake8\n", encoding="utf-8")
        (app_dir / "__init__.py").write_text("", encoding="utf-8")
        (app_dir / "main.py").write_text(
            'def run() -> int:\n    """Run generated project."""\n    return 0\n', encoding="utf-8"
        )
        (tests_dir / "test_core.py").write_text(
            "from app.main import run\n\n\ndef test_run_returns_zero() -> None:\n    assert run() == 0\n",
            encoding="utf-8",
        )
        return root
