"""SQLite-based memory system."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import ProjectCategory, RunRecord


class MemoryStore:
    """Persistence layer for generated ideas and run history."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    name TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    complexity INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT NOT NULL,
                    project_name TEXT NOT NULL,
                    retries INTEGER NOT NULL,
                    success INTEGER NOT NULL
                )
                """
            )

    def list_project_names(self) -> set[str]:
        """Return all generated project names."""
        with self._connect() as conn:
            rows = conn.execute("SELECT name FROM projects").fetchall()
        return {row[0] for row in rows}

    def store_project(self, name: str, category: ProjectCategory, complexity: int) -> None:
        """Persist a project idea so duplicates are avoided."""
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO projects(name, category, complexity) VALUES(?, ?, ?)",
                (name, category.value, complexity),
            )

    def store_run(self, run: RunRecord) -> None:
        """Persist run metadata for historical tracking."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runs(started_at, finished_at, project_name, retries, success)
                VALUES(?, ?, ?, ?, ?)
                """,
                (
                    run.started_at.isoformat(),
                    run.finished_at.isoformat(),
                    run.project_name,
                    run.retries,
                    int(run.success),
                ),
            )
