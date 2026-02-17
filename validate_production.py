#!/usr/bin/env python
"""Production readiness validation script."""

import subprocess
import sys
from pathlib import Path


def run_check(name: str, command: list[str], exit_on_fail: bool = False) -> bool:
    """Run a check command and report status."""
    try:
        result = subprocess.run(command, capture_output=True, timeout=30)
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"  [{status}] {name}")
        if result.returncode != 0 and exit_on_fail:
            print(f"       Error: {result.stderr.decode()[:100]}")
            return False
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {name}")
        return False
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return False


def check_files() -> bool:
    """Check that all required files exist."""
    print("\n=== Checking Required Files ===")
    required_files = [
        "main.py",
        "Dockerfile",
        "docker-compose.yml",
        "Makefile",
        "requirements.txt",
        ".env.example",
        ".dockerignore",
        "PRODUCTION_GUIDE.md",
        "DEPLOYMENT_CHECKLIST.md",
        "PRODUCTION_READY.md",
        "app/logging_config.py",
        "app/health.py",
        "app/backup.py",
        ".github/workflows/ci-cd.yml",
    ]
    
    all_good = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {file_path}")
        if not exists:
            all_good = False
    return all_good


def check_dependencies() -> bool:
    """Check that all dependencies are installed."""
    print("\n=== Checking Dependencies ===")
    required_deps = [
        ("pytest", True),
        ("pytest-cov", True),
        ("flake8", True),
        ("mypy", True),
        ("GitPython", False),  # Optional
    ]
    
    all_good = True
    for dep, required in required_deps:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", dep],
            capture_output=True,
            timeout=10,
        )
        if result.returncode == 0:
            print(f"  [INSTALLED] {dep}")
        else:
            status = "MISSING (required)" if required else "MISSING (optional)"
            print(f"  [{status}] {dep}")
            if required:
                all_good = False
    return all_good


def check_code_quality() -> bool:
    """Run code quality checks."""
    print("\n=== Running Code Quality Checks ===")
    
    checks = [
        ("Tests", [sys.executable, "-m", "pytest", "-q", "--tb=short"], True),
        ("Linting", [sys.executable, "-m", "flake8", "app", "tests", "--count", "--max-line-length=127"], False),
        ("Type Checking", [sys.executable, "-m", "mypy", "app", "--ignore-missing-imports"], False),
    ]
    
    all_good = True
    for name, cmd, required in checks:
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            status = "PASS" if result.returncode == 0 else "FAIL"
            optional = "" if required else " (optional)"
            print(f"  [{status}] {name}{optional}")
            if result.returncode != 0 and required:
                all_good = False
        except Exception as e:
            optional = "" if required else " (optional)"
            print(f"  [ERROR] {name}: {str(e)[:50]}{optional}")
            if required:
                all_good = False
    return all_good


def check_logging() -> bool:
    """Check logging infrastructure."""
    print("\n=== Checking Logging Infrastructure ===")
    try:
        from app.logging_config import configure_logging, get_logger
        from pathlib import Path
        
        configure_logging(log_dir=Path("logs"))
        logger = get_logger("check")
        logger.info("Test log message")
        
        logs_dir = Path("logs")
        log_files = list(logs_dir.glob("*.log"))
        
        if log_files:
            print(f"  [OK] Logging configured ({len(log_files)} log files)")
            return True
        else:
            print(f"  [FAIL] No log files created")
            return False
    except Exception as e:
        print(f"  [ERROR] Logging check failed: {e}")
        return False


def check_health() -> bool:
    """Check health system."""
    print("\n=== Checking Health System ===")
    try:
        from app.health import HealthChecker
        from app.config import AgentConfig
        
        config = AgentConfig()
        config.ensure_dirs()
        checker = HealthChecker(config.memory_db_path, config.workspace_root)
        health = checker.check()
        
        if health.status == "unhealthy":
            print(f"  [FAIL] Unhealthy: {health.details}")
            return False
        
        print(f"  [OK] Health status: {health.status}")
        for check, status in health.checks.items():
            print(f"       {check}: {status}")
        return True
    except Exception as e:
        print(f"  [ERROR] Health check failed: {e}")
        return False


def check_backup() -> bool:
    """Check backup system."""
    print("\n=== Checking Backup System ===")
    try:
        from app.backup import DatabaseBackup
        from app.config import AgentConfig
        
        config = AgentConfig()
        config.ensure_dirs()
        backup = DatabaseBackup(config.memory_db_path)
        
        if not backup.verify_database():
            print("  [FAIL] Database verification failed")
            return False
        
        print("  [OK] Database integrity verified")
        
        backups = backup.list_backups()
        print(f"  [OK] {len(backups)} backups available")
        return True
    except Exception as e:
        print(f"  [ERROR] Backup check failed: {e}")
        return False


def main() -> int:
    """Run all production readiness checks."""
    print("=" * 60)
    print("AutoDev Agent - Production Readiness Validation")
    print("=" * 60)
    
    all_checks = [
        ("File Structure", check_files),
        ("Dependencies", check_dependencies),
        ("Code Quality", check_code_quality),
        ("Logging", check_logging),
        ("Health System", check_health),
        ("Backup System", check_backup),
    ]
    
    results = {}
    for name, check_func in all_checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\nUnexpected error in {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n[SUCCESS] Project is PRODUCTION READY!")
        return 0
    else:
        print(f"\n[FAILED] {total - passed} check(s) failed. Please fix before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
