"""Health check and monitoring utilities."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(slots=True)
class HealthStatus:
    """Current health status of the system."""

    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: str
    checks: dict[str, str]  # Check name -> status
    details: dict[str, str] = None  # type: ignore


class HealthChecker:
    """Perform system health checks."""

    def __init__(self, memory_db_path: Path, workspace_root: Path) -> None:
        self.memory_db_path = memory_db_path
        self.workspace_root = workspace_root

    def check(self) -> HealthStatus:
        """Run all health checks."""
        checks = {}
        checks["memory_db"] = self._check_memory_db()
        checks["workspace"] = self._check_workspace()
        checks["disk_space"] = self._check_disk_space()

        failed = [name for name, status in checks.items() if status != "ok"]
        status_str = "unhealthy" if len(failed) > 1 else "degraded" if failed else "healthy"

        return HealthStatus(
            status=status_str,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
            checks=checks,
            details={"failed_checks": failed} if failed else {},
        )

    def _check_memory_db(self) -> str:
        """Check if memory database is accessible."""
        try:
            if not self.memory_db_path.parent.exists():
                return "db_dir_missing"
            # Try to connect
            import sqlite3

            try:
                conn = sqlite3.connect(self.memory_db_path)
                conn.execute("SELECT 1")
                conn.close()
                return "ok"
            except sqlite3.Error:
                return "db_corrupted"
        except Exception:
            return "error"

    def _check_workspace(self) -> str:
        """Check if workspace directory is writable."""
        try:
            if not self.workspace_root.exists():
                self.workspace_root.mkdir(parents=True, exist_ok=True)
            test_file = self.workspace_root / ".health_check"
            test_file.touch()
            test_file.unlink()
            return "ok"
        except Exception:
            return "not_writable"

    def _check_disk_space(self) -> str:
        """Check if sufficient disk space is available."""
        try:
            import shutil

            stat = shutil.disk_usage(self.workspace_root)
            # Require at least 100MB free
            if stat.free < 100 * 1024 * 1024:
                return "low_space"
            return "ok"
        except Exception:
            return "error"

    def to_json(self, health: HealthStatus) -> str:
        """Serialize health status to JSON."""
        health_dict = asdict(health)
        return json.dumps(health_dict, indent=2)
