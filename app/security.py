"""Security policy checks for generated projects."""

from __future__ import annotations

from pathlib import Path


class SecurityPolicyError(RuntimeError):
    """Raised when a generated project violates security policy."""


class SecurityScanner:
    """Minimal static checks for dangerous patterns in generated code."""

    FORBIDDEN_PATTERNS = (
        "subprocess.Popen(",
        "os.system(",
        "eval(",
        "exec(",
    )

    def scan(self, project_root: Path) -> None:
        """Raise on disallowed patterns in python source files."""
        violations: list[str] = []
        for file_path in project_root.rglob("*.py"):
            content = file_path.read_text(encoding="utf-8")
            for pattern in self.FORBIDDEN_PATTERNS:
                if pattern in content:
                    violations.append(f"{file_path}: {pattern}")
        if violations:
            joined = "; ".join(violations)
            raise SecurityPolicyError(f"Security policy violation: {joined}")
