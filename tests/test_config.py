from app.config import AgentConfig


def test_config_from_env(monkeypatch) -> None:
    monkeypatch.setenv("AUTODEV_MAX_RETRIES", "5")
    monkeypatch.setenv("AUTODEV_RUN_LINT", "false")
    cfg = AgentConfig.from_env()
    assert cfg.max_retries == 5
    assert cfg.run_lint is False
