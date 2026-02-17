"""Database backup and recovery utilities."""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class DatabaseBackup:
    """Handle SQLite database backups and recovery."""

    def __init__(self, db_path: Path, backup_dir: Path = None) -> None:
        self.db_path = db_path
        self.backup_dir = backup_dir or db_path.parent / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, description: str = "") -> Path:
        """Create a backup of the database file."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(self.db_path, backup_path)

        # Store metadata
        metadata_file = backup_path.with_suffix(".md")
        metadata = f"Backup: {backup_name}\nTimestamp: {timestamp}\nDescription: {description}\n"
        metadata_file.write_text(metadata)

        return backup_path

    def restore_backup(self, backup_path: Path) -> None:
        """Restore database from a backup."""
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        # Create a safety backup of current db
        if self.db_path.exists():
            safety_backup = self.backup_dir / "pre_restore_backup.db"
            shutil.copy2(self.db_path, safety_backup)

        # Restore
        shutil.copy2(backup_path, self.db_path)

    def verify_database(self) -> bool:
        """Verify database integrity."""
        if not self.db_path.exists():
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            # Run integrity check
            result = conn.execute("PRAGMA integrity_check").fetchone()
            conn.close()
            return result[0] == "ok"
        except sqlite3.Error:
            return False

    def list_backups(self) -> list[tuple[Path, datetime]]:
        """List all available backups with their timestamps."""
        backups = []
        for backup_file in sorted(self.backup_dir.glob("backup_*.db"), reverse=True):
            try:
                # Parse timestamp from filename
                timestamp_str = backup_file.stem.replace("backup_", "")
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                backups.append((backup_file, timestamp))
            except ValueError:
                continue
        return backups

    def cleanup_old_backups(self, keep_count: int = 10) -> None:
        """Cleanup old backups, keeping only the most recent ones."""
        backups = self.list_backups()
        if len(backups) > keep_count:
            for backup_path, _ in backups[keep_count:]:
                backup_path.unlink()
                backup_path.with_suffix(".md").unlink(missing_ok=True)
