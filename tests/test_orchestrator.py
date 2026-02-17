from app.config import AgentConfig
from app.orchestrator import AutoDevOrchestrator


def test_orchestrator_run_once_success(tmp_path) -> None:
    config = AgentConfig(
        memory_db_path=tmp_path / "state" / "memory.db",
        workspace_root=tmp_path / "generated_projects",
        schedule_lock_file=tmp_path / "state" / "scheduler.lock",
        run_lint=False,
        run_coverage=False,
        strict_validation=True,
        max_retries=1,
    )
    orchestrator = AutoDevOrchestrator(config)
    assert orchestrator.run_once() is True
