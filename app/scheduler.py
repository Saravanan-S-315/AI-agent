"""Scheduler lock controls to avoid duplicate runs."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass(slots=True)
class SchedulerLock:
    """Lock-file based scheduler guard with stale-lock recovery."""

    lock_file: Path
    stale_after_seconds: int = 3600

    def acquire(self) -> bool:
        """Acquire run lock. Returns False if a fresh lock already exists."""
        if self.lock_file.exists() and not self._is_stale():
            return False

        payload = {
            "pid": os.getpid(),
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        self.lock_file.write_text(json.dumps(payload), encoding="utf-8")
        return True

    def release(self) -> None:
        """Release run lock safely."""
        if self.lock_file.exists():
            self.lock_file.unlink()

    def _is_stale(self) -> bool:
        """Whether lock file is considered stale and can be replaced."""
        try:
            payload = json.loads(self.lock_file.read_text(encoding="utf-8"))
            created_at = datetime.fromisoformat(payload["created_at"])
        except (json.JSONDecodeError, KeyError, ValueError):
            return True

        age_limit = datetime.now(tz=timezone.utc) - timedelta(seconds=self.stale_after_seconds)
        return created_at <= age_limit
