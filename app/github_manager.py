"""GitHub pull request creation helper."""

from __future__ import annotations

import json
import os
import urllib.request


class GitHubManager:
    """Minimal GitHub API integration for pull request creation."""

    def __init__(self, repo: str) -> None:
        self.repo = repo
        self.token = os.getenv("GITHUB_TOKEN", "")

    def create_pull_request(self, *, title: str, body: str, head: str, base: str = "main") -> dict:
        """Create a GitHub pull request and return API response payload."""
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN is not set.")
        if not self.repo:
            raise RuntimeError("Target GitHub repository is not configured.")

        payload = json.dumps({"title": title, "body": body, "head": head, "base": base}).encode("utf-8")
        request = urllib.request.Request(
            url=f"https://api.github.com/repos/{self.repo}/pulls",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "autodev-agent",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
