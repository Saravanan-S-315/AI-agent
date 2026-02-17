"""Project code generation and scaffolding utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import AgentConfig
from .models import PlanArtifact, ProjectIdea


@dataclass(slots=True)
class GeneratedProject:
    """Generated project metadata."""

    root: Path
    files: list[Path]


class ProjectScaffolder:
    """Generate a runnable modular project from plan + idea."""

    def generate(
        self,
        *,
        workspace_root: Path,
        idea: ProjectIdea,
        plan: PlanArtifact,
        readme_text: str,
        config: AgentConfig,
    ) -> GeneratedProject:
        root = workspace_root / idea.name
        app_dir = root / "app"
        tests_dir = root / "tests"
        app_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)

        written: list[Path] = []
        written.append(self._write(root / "README.md", readme_text, config))
        written.append(self._write(root / "requirements.txt", "pytest\npytest-cov\nflake8\n", config))
        written.append(self._write(app_dir / "__init__.py", "", config))
        written.append(self._write(app_dir / "models.py", self._models_content(), config))
        written.append(self._write(app_dir / "services.py", self._services_content(), config))
        written.append(self._write(app_dir / "main.py", self._main_content(idea), config))
        written.append(self._write(tests_dir / "test_core.py", self._tests_content(), config))
        written.append(self._write(root / "pytest.ini", "[pytest]\npythonpath = .\ntestpaths = tests\n", config))

        if len(written) > config.max_files:
            raise ValueError("Generated files exceed configured max_files.")
        return GeneratedProject(root=root, files=written)

    @staticmethod
    def _write(path: Path, content: str, config: AgentConfig) -> Path:
        line_count = max(content.count("\n"), 1)
        if line_count > config.max_lines_per_file:
            raise ValueError(f"Generated file {path} exceeds line limit.")
        path.write_text(content, encoding="utf-8")
        return path

    @staticmethod
    def _models_content() -> str:
        return (
            '"""Generated domain models."""\n\n'
            "from dataclasses import dataclass\n\n\n"
            "@dataclass(slots=True)\n"
            "class ExecutionResult:\n"
            "    status: str\n"
            "    processed_items: int\n"
        )

    @staticmethod
    def _services_content() -> str:
        return (
            '"""Generated service layer."""\n\n'
            "from .models import ExecutionResult\n\n\n"
            "def execute(payload: dict[str, int]) -> ExecutionResult:\n"
            "    \"\"\"Execute business logic with input validation.\"\"\"\n"
            "    if payload.get('items', 0) < 0:\n"
            "        raise ValueError('items must be non-negative')\n"
            "    return ExecutionResult(status='ok', processed_items=payload.get('items', 0))\n"
        )

    @staticmethod
    def _main_content(idea: ProjectIdea) -> str:
        return (
            '"""Generated entrypoint for project."""\n\n'
            "from .services import execute\n\n\n"
            "def run() -> int:\n"
            f"    \"\"\"Run workflow for {idea.name}.\"\"\"\n"
            "    result = execute({'items': 1})\n"
            "    return 0 if result.status == 'ok' else 1\n"
        )

    @staticmethod
    def _tests_content() -> str:
        return (
            "from app.main import run\n"
            "from app.services import execute\n\n\n"
            "def test_run_returns_success_code() -> None:\n"
            "    assert run() == 0\n\n\n"
            "def test_execute_rejects_negative_items() -> None:\n"
            "    try:\n"
            "        execute({'items': -1})\n"
            "    except ValueError as exc:\n"
            "        assert 'non-negative' in str(exc)\n"
            "    else:\n"
            "        raise AssertionError('expected ValueError')\n"
        )
