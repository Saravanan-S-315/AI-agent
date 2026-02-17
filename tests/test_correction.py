from app.correction import CorrectionEngine
from app.models import ValidationResult


def test_correction_engine_repairs_missing_test_signature(tmp_path) -> None:
    project = tmp_path / "proj"
    tests_dir = project / "tests"
    tests_dir.mkdir(parents=True)
    test_file = tests_dir / "test_core.py"
    test_file.write_text("def test_placeholder() -> None:\n    assert True\n", encoding="utf-8")

    result = ValidationResult(success=False, checks={"tests": False}, logs=[])
    CorrectionEngine().apply(project, result)

    assert "test_run_returns_success_code" in test_file.read_text(encoding="utf-8")
