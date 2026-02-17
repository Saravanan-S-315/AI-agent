"""Git workflow helpers for branch-first development."""

from __future__ import annotations

import subprocess


class GitWorkflow:
    """Encapsulates basic branch and commit operations."""

    @staticmethod
    def create_feature_branch(name: str) -> str:
        branch = f"feature/{name}"
        subprocess.run(["git", "checkout", "-b", branch], check=True)
        return branch

    @staticmethod
    def commit_project(project_name: str) -> None:
        message = f"feat: add {project_name} with tests and documentation"
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
