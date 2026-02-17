"""CLI entrypoint for AutoDev Agent."""

from app.config import AgentConfig
from app.orchestrator import AutoDevOrchestrator


def main() -> int:
    """Run one autonomous development cycle."""
    orchestrator = AutoDevOrchestrator(AgentConfig.from_env())
    return 0 if orchestrator.run_once() else 1


if __name__ == "__main__":
    raise SystemExit(main())
