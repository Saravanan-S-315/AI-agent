.PHONY: help setup test lint format type-check security-scan run run-docker docker-build docker-push clean health-check backup restore logs

help:
	@echo "AutoDev Agent - Make targets"
	@echo ""
	@echo "Development:"
	@echo "  make setup          - Setup development environment"
	@echo "  make test           - Run test suite with coverage"
	@echo "  make lint           - Run flake8 linting"
	@echo "  make format         - Format code with black"
	@echo "  make type-check     - Run mypy type checking"
	@echo "  make security-scan  - Run security checks"
	@echo ""
	@echo "Operations:"
	@echo "  make run            - Run orchestrator once"
	@echo "  make run-docker     - Run using Docker Compose"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-push    - Push Docker image to registry"
	@echo "  make health-check   - Check system health"
	@echo ""
	@echo "Maintenance:"
	@echo "  make backup         - Create database backup"
	@echo "  make restore        - Restore from backup"
	@echo "  make logs           - Show recent logs"
	@echo "  make clean          - Clean generated artifacts"

setup:
	python -m venv .venv
	. .venv/Scripts/activate && pip install --upgrade pip setuptools wheel
	. .venv/Scripts/activate && pip install -r requirements.txt
	@echo "Setup complete! Activate with: source .venv/Scripts/activate"

test:
	pytest -v --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80

lint:
	flake8 app tests --count --max-complexity=10 --max-line-length=127

format:
	black app tests main.py --line-length=127
	isort app tests main.py

type-check:
	mypy app --ignore-missing-imports

security-scan:
	python -m pip check
	python -c "from app.security import SecurityScanner; from pathlib import Path; s = SecurityScanner(); print('Security patterns configured:', s.FORBIDDEN_PATTERNS)"

run:
	python main.py

run-ui:
	python run_ui.py

run-docker:
	docker-compose up -d
	docker-compose logs -f

docker-build:
	docker build -t autodev-agent:latest .

docker-push:
	docker tag autodev-agent:latest ghcr.io/$(GITHUB_REPO):latest
	docker push ghcr.io/$(GITHUB_REPO):latest

health-check:
	python -c "\
	from app.health import HealthChecker;\
	from app.config import AgentConfig;\
	c = AgentConfig();\
	c.ensure_dirs();\
	h = HealthChecker(c.memory_db_path, c.workspace_root);\
	health = h.check();\
	print(f'Status: {health.status}');\
	print(f'Checks: {health.checks}');\
	exit(0 if health.status != 'unhealthy' else 1)"

backup:
	python -c "\
	from app.backup import DatabaseBackup;\
	from app.config import AgentConfig;\
	b = DatabaseBackup(AgentConfig().memory_db_path);\
	bpath = b.create_backup('Manual backup from make');\
	print(f'Backup created: {bpath}')"

restore:
	@echo "Available backups:"
	python -c "\
	from app.backup import DatabaseBackup;\
	from app.config import AgentConfig;\
	b = DatabaseBackup(AgentConfig().memory_db_path);\
	for path, ts in b.list_backups()[:5]:\
		print(f'  {path} ({ts})')"
	@echo "Run: python -c \"from app.backup import DatabaseBackup; from app.config import AgentConfig; DatabaseBackup(AgentConfig().memory_db_path).restore_backup(<backup_path>)\""

logs:
	tail -n 50 logs/autodev.log

clean:
	rm -rf build dist .eggs *.egg-info
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

all: clean setup lint type-check test
	@echo "All checks passed!"
