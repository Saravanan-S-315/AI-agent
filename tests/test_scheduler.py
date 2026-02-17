import json
from datetime import datetime, timedelta, timezone

from app.scheduler import SchedulerLock


def test_scheduler_lock_acquire_release(tmp_path) -> None:
    lock = SchedulerLock(tmp_path / "lock")
    assert lock.acquire() is True
    assert lock.acquire() is False
    lock.release()
    assert lock.acquire() is True


def test_scheduler_reclaims_stale_lock(tmp_path) -> None:
    lock_path = tmp_path / "lock"
    stale_payload = {
        "pid": 999,
        "created_at": (datetime.now(tz=timezone.utc) - timedelta(hours=2)).isoformat(),
    }
    lock_path.write_text(json.dumps(stale_payload), encoding="utf-8")

    lock = SchedulerLock(lock_path, stale_after_seconds=60)
    assert lock.acquire() is True
