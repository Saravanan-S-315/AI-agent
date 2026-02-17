"""Validation layer for generated projects."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .models import ValidationResult


class Validator:
    """Runs syntax, lint, tests, and optional quality checks before commit."""

    def run(
        self,
        project_root: Path,
        *,
        run_lint: bool = True,
        run_type_check: bool = False,
        run_coverage: bool = True,
        min_coverage: int = 85,
        strict_validation: bool = True,
    ) -> ValidationResult:
        """Execute validation commands and collect status."""
        checks: dict[str, bool] = {}
        logs: list[str] = []

        checks["syntax"] = self._run_command(["python", "-m", "compileall", "app"], project_root, logs)
        if run_lint:
            checks["lint"] = self._run_command([sys.executable, "-m", "flake8", "app", "tests"], project_root, logs)
        if run_coverage:
            checks["coverage"] = self._run_command(
                [sys.executable, "-m", "pytest", "-q", "--cov=app", f"--cov-fail-under={min_coverage}"], project_root, logs
            )
        else:
            checks["tests"] = self._run_command([sys.executable, "-m", "pytest", "-q"], project_root, logs)
        if run_type_check:
            checks["typecheck"] = self._run_command([sys.executable, "-m", "mypy", "app"], project_root, logs)

        success = all(checks.values())
        if not strict_validation and "lint" in checks and not checks["lint"]:
            success = all(value for key, value in checks.items() if key != "lint")
        return ValidationResult(success=success, checks=checks, logs=logs)

    @staticmethod
    def _run_command(command: list[str], cwd: Path, logs: list[str]) -> bool:
        logs.append(f"$ {' '.join(command)}")
        try:
            env = {**os.environ, "PYTHONPATH": str(cwd)}
            result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            logs.append(f"Missing command: {command[0]}")
            return False
        if result.stdout:
            logs.append(result.stdout.strip())
        if result.stderr:
            logs.append(result.stderr.strip())
        return result.returncode == 0
