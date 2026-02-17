"""Architecture planning module."""

from __future__ import annotations

from .config import AgentConfig
from .models import PlanArtifact, ProjectIdea


class ArchitecturePlanner:
    """Builds a modular implementation plan for each idea."""

    def create_plan(self, idea: ProjectIdea, config: AgentConfig) -> PlanArtifact:
        """Generate a folder structure and implementation outline."""
        structure = [
            f"{idea.name}/",
            f"{idea.name}/app/",
            f"{idea.name}/app/main.py",
            f"{idea.name}/app/services.py",
            f"{idea.name}/app/models.py",
            f"{idea.name}/tests/test_core.py",
            f"{idea.name}/README.md",
            f"{idea.name}/requirements.txt",
        ][: config.max_files]

        dependencies = ["pytest>=8.0.0"]
        interfaces = [
            "main.run() -> int",
            "services.execute(payload: dict) -> dict",
            "models.Record dataclass",
        ]
        test_outline = [
            "Validate happy-path command execution",
            "Validate invalid payload handling",
            "Validate deterministic output format",
        ]
        return PlanArtifact(structure, dependencies, interfaces, test_outline)
