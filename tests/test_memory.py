from datetime import datetime, timezone

from app.memory import MemoryStore
from app.models import ProjectCategory, RunRecord


def test_memory_store_round_trip(tmp_path) -> None:
    db = tmp_path / "memory.db"
    store = MemoryStore(db)
    store.store_project("demo", ProjectCategory.CLI, 2)
    assert "demo" in store.list_project_names()

    now = datetime.now(tz=timezone.utc)
    store.store_run(
        RunRecord(started_at=now, finished_at=now, project_name="demo", retries=0, success=True)
    )
