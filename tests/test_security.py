import pytest

from app.security import SecurityPolicyError, SecurityScanner


def test_security_scanner_detects_forbidden_patterns(tmp_path) -> None:
    project = tmp_path / "proj"
    app_dir = project / "app"
    app_dir.mkdir(parents=True)
    (app_dir / "danger.py").write_text("import os\nos.system('echo hi')\n", encoding="utf-8")

    with pytest.raises(SecurityPolicyError):
        SecurityScanner().scan(project)
