"""Git workflow helpers for branch-first development."""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitWorkflow:
    """Encapsulates branch and commit operations."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def create_or_checkout_feature_branch(self, name: str) -> str:
        branch = f"feature/{name}"
        existing = subprocess.run(
            ["git", "rev-parse", "--verify", branch], cwd=self.repo_root, capture_output=True, text=True
        )
        if existing.returncode == 0:
            subprocess.run(["git", "checkout", branch], cwd=self.repo_root, check=True)
        else:
            subprocess.run(["git", "checkout", "-b", branch], cwd=self.repo_root, check=True)
        return branch

    def commit_project(self, project_name: str) -> bool:
        message = f"feat: add {project_name} with tests and documentation"
        subprocess.run(["git", "add", "-A"], cwd=self.repo_root, check=True)
        staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=self.repo_root)
        if staged.returncode == 0:
            return False
        subprocess.run(["git", "commit", "-m", message], cwd=self.repo_root, check=True)
        return True

    def push_branch(self, branch: str, remote: str = "origin") -> None:
        subprocess.run(["git", "push", "-u", remote, branch], cwd=self.repo_root, check=True)
