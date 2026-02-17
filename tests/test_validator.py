from pathlib import Path

from app.validator import Validator


def test_validator_reports_missing_commands(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    (project / "app").mkdir(parents=True)
    (project / "tests").mkdir(parents=True)
    (project / "app" / "__init__.py").write_text("", encoding="utf-8")
    (project / "app" / "main.py").write_text("def run() -> int:\n    return 0\n", encoding="utf-8")
    (project / "tests" / "test_core.py").write_text(
        "from app.main import run\n\n\ndef test_run() -> None:\n    assert run() == 0\n", encoding="utf-8"
    )

    result = Validator().run(
        project,
        run_lint=False,
        run_coverage=False,
        run_type_check=False,
    )

    assert result.checks["syntax"] is True
    assert result.checks["tests"] is True
    assert result.success is True
