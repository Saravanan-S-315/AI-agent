# AutoDev Agent - User Interface Guide

## Overview

AutoDev Agent is a **command-line (CLI) based** application. There is no graphical web UI by default, but multiple interfaces exist for interaction:

## 1. 📟 Command-Line Interface (CLI)

### Primary Interface: `python main.py`

This is the main execution command:

```bash
python main.py
```

**Output:**
```
[2026-02-17 16:01:34] autodev.main - INFO - AutoDev Agent starting...
[2026-02-17 16:01:34] autodev.main - INFO - Health status: healthy
[2026-02-17 16:01:34] autodev.orchestrator - INFO - Starting orchestration cycle
[2026-02-17 16:01:34] autodev.orchestrator - INFO - Generated project idea: habit-api
[2026-02-17 16:01:34] autodev.orchestrator - INFO - Project scaffolded at: generated_projects\habit-api
[2026-02-17 16:01:34] autodev.orchestrator - INFO - Security scan passed
[2026-02-17 16:01:37] autodev.orchestrator - INFO - Running validation (attempt 1/4)...
[2026-02-17 16:01:39] autodev.orchestrator - INFO - Validation passed
[2026-02-17 16:01:39] autodev.main - INFO - Orchestration cycle completed successfully
```

**Exit Codes:**
- `0` = Success (project generated and validated)
- `1` = Failure (validation failed or system unhealthy)

### Available Make Commands

```bash
make help              # Show all available commands
make setup             # Setup development environment
make test              # Run tests
make lint              # Code quality checks
make format            # Format code
make type-check        # Type validation
make run               # Execute once
make docker-build      # Build container
make health-check      # Check system health
make backup            # Create database backup
make restore           # Restore from backup
make logs              # Show recent logs
make clean             # Clean artifacts
```

## 2. ⚙️ Configuration Interface: `.env` file

This is how you **configure** the agent's behavior:

### Setup Configuration

```bash
# Copy the template
cp .env.example .env

# Edit with your settings
nano .env  # or your editor
```

### Example `.env` Configuration

```ini
# Project Complexity (1-5, higher = more complex projects)
AUTODEV_MIN_COMPLEXITY=1
AUTODEV_MAX_COMPLEXITY=5

# Validation Settings
AUTODEV_MAX_RETRIES=3
AUTODEV_MIN_COVERAGE=85

# Feature Toggles
AUTODEV_RUN_LINT=true
AUTODEV_RUN_TYPECHECK=false
AUTODEV_RUN_COVERAGE=true
AUTODEV_STRICT_VALIDATION=true

# Scheduler Settings
AUTODEV_LOCK_STALE_SECONDS=3600

# Git Automation (Optional)
AUTODEV_AUTO_GIT=false
AUTODEV_AUTO_PR=false

# GitHub Integration (Optional)
# AUTODEV_GITHUB_REPO=owner/repo
# GITHUB_TOKEN=ghp_xxxx
```

### Change Configuration Without File

```bash
# Override via environment variables
AUTODEV_MAX_COMPLEXITY=3 python main.py

# Disable linting
AUTODEV_RUN_LINT=false python main.py

# Increase retries
AUTODEV_MAX_RETRIES=5 python main.py
```

## 3. 📁 File-Based Interface: Generated Projects

All output is stored as **files in the filesystem**:

### Generated Project Structure

```
generated_projects/
├── habit-api/                    # ← Generated project
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Entry point - READ THIS
│   │   ├── models.py            # Data models
│   │   └── services.py          # Business logic
│   ├── tests/
│   │   └── test_core.py         # Test cases
│   ├── README.md                # Documentation - READ THIS
│   ├── requirements.txt         # Dependencies
│   ├── pytest.ini               # Test config
│   └── validation_log.jsonl     # Validation history
├── csv-inspector/
│   └── [similar structure]
└── log-summarizer/
    └── [similar structure]
```

### Access Generated Projects

```bash
# View project list
ls generated_projects/

# View project code
cat generated_projects/habit-api/app/main.py

# View documentation
cat generated_projects/habit-api/README.md

# Run project tests
cd generated_projects/habit-api
python -m pytest tests/

# View validation history
cat generated_projects/habit-api/validation_log.jsonl
```

## 4. 📊 Logging Interface: Log Files

View execution history via **log files**:

### Log Files Location

```
logs/
├── autodev.log         # Main application log (rotating, 10MB)
├── errors.log          # Errors only (separate)
└── *.md               # Backup metadata
```

### View Logs

```bash
# Real-time tail
tail -f logs/autodev.log

# View errors only
tail -f logs/errors.log

# View last 50 lines
tail -50 logs/autodev.log

# Search logs
grep "ERROR" logs/autodev.log
grep "generated" logs/autodev.log
```

### Log Format

```
[2026-02-17 16:01:34] autodev.orchestrator - INFO - Generated project idea: habit-api
[2026-02-17 16:01:37] autodev.orchestrator - WARNING - Validation failed: {'syntax': True, 'lint': False}
[2026-02-17 16:01:39] autodev.orchestrator - ERROR - Security policy violation
```

## 5. 🔧 Database Interface: Direct Queries

Query the **SQLite database** directly:

### Check Project History

```bash
python -c "
from app.memory import MemoryStore
from app.config import AgentConfig

memory = MemoryStore(AgentConfig().memory_db_path)
projects = memory.list_project_names()
print(f'Generated projects: {projects}')
"
```

### View Run History

```bash
python -c "
import sqlite3
from app.config import AgentConfig

conn = sqlite3.connect(AgentConfig().memory_db_path)
cursor = conn.execute('SELECT * FROM runs ORDER BY id DESC LIMIT 5')
for row in cursor:
    print(f'Run {row[0]}: {row[3]} - Success: {bool(row[5])} - Retries: {row[4]}')
conn.close()
"
```

### Check Database

```bash
python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig

backup = DatabaseBackup(AgentConfig().memory_db_path)
if backup.verify_database():
    print('Database: OK')
else:
    print('Database: CORRUPTED')
"
```

## 6. 🏥 Health Check Interface

Monitor system **health status**:

### Check Health

```bash
# Quick health check
make health-check

# Detailed health output
python -c "
from app.health import HealthChecker
from app.config import AgentConfig

config = AgentConfig()
checker = HealthChecker(config.memory_db_path, config.workspace_root)
health = checker.check()
print(f'Status: {health.status}')
for check, status in health.checks.items():
    print(f'  {check}: {status}')
"
```

### Health Status Meanings

- ✅ **healthy** - All systems operational
- ⚠️ **degraded** - One check failing (still operational)
- 🔴 **unhealthy** - Multiple failures (action needed)

## 7. 💾 Backup Interface

Manage **database backups**:

### Create Backup

```bash
make backup

# Or programmatically
python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig

backup = DatabaseBackup(AgentConfig().memory_db_path)
backup_path = backup.create_backup('before-update')
print(f'Backup: {backup_path}')
"
```

### List Backups

```bash
python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig

backup = DatabaseBackup(AgentConfig().memory_db_path)
for path, timestamp in backup.list_backups()[:10]:
    print(f'{path}: {timestamp}')
"
```

### Restore Backup

```bash
python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig
from pathlib import Path

backup = DatabaseBackup(AgentConfig().memory_db_path)
backup_path = Path('state/backups/backup_20260217_120000.db')
backup.restore_backup(backup_path)
print('Restored!')
"
```

## 8. 🐳 Docker Interface

Use Docker for **containerized execution**:

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f autodev-agent

# Check status
docker-compose ps

# Stop services
docker-compose down
```

### Docker Commands

```bash
# Build image
docker build -t autodev-agent:latest .

# Run container
docker run -v $(pwd)/logs:/app/logs autodev-agent:latest

# View output
docker logs <container-id>
```

## 9. 🐚 Shell/Script Interface

**Automate** via shell scripts:

### Simple Script

```bash
#!/bin/bash
# run_agent.sh

cd /path/to/autodev

# Check health
python -c "from app.health import HealthChecker; ..." || exit 1

# Run agent
python main.py
EXIT_CODE=$?

# Log result
if [ $EXIT_CODE -eq 0 ]; then
    echo "SUCCESS" >> run.log
else
    echo "FAILED" >> run.log
fi

exit $EXIT_CODE
```

### Cron Schedule

```bash
# Run every 4 hours
0 */4 * * * cd /path/to/autodev && python main.py >> logs/cron.log 2>&1

# Run daily at 2 AM
0 2 * * * cd /path/to/autodev && python main.py

# Run every hour
0 * * * * cd /path/to/autodev && make health-check
```

## 10. 🐍 Python API Interface

Use as a **Python library**:

### Import and Use

```python
from app.orchestrator import AutoDevOrchestrator
from app.config import AgentConfig
from app.health import HealthChecker
from app.backup import DatabaseBackup

# Create config
config = AgentConfig()

# Check health
checker = HealthChecker(config.memory_db_path, config.workspace_root)
health = checker.check()
if health.status == "unhealthy":
    print(f"System unhealthy: {health.details}")
    exit(1)

# Run orchestrator
orchestrator = AutoDevOrchestrator(config)
success = orchestrator.run_once()

# Create backup
backup = DatabaseBackup(config.memory_db_path)
backup_path = backup.create_backup("after-run")

print(f"Success: {success}, Backup: {backup_path}")
```

### Integrate with Other Tools

```python
# Use in FastAPI
from fastapi import FastAPI
from app.orchestrator import AutoDevOrchestrator

app = FastAPI()

@app.post("/generate")
async def generate_project():
    orchestrator = AutoDevOrchestrator()
    success = orchestrator.run_once()
    return {"success": success}

# Use in Flask
# Use in Django management command
# Use in other frameworks
```

## Quick Reference

| Interface | Access | Use Case |
|-----------|--------|----------|
| **CLI** | `python main.py` | Execute agent |
| **Config** | `.env` file | Configure behavior |
| **Files** | `generated_projects/` | View output |
| **Logs** | `logs/` directory | Debug/monitor |
| **Health** | `make health-check` | Status check |
| **Backup** | `make backup` | Data protection |
| **Docker** | `docker-compose up` | Container deploy |
| **Python API** | `from app import ...` | Programmatic use |
| **Database** | SQLite CLI | Raw queries |
| **Shell** | bash scripts | Automation |

## Getting Started - 3 Steps

### Step 1: Configure
```bash
cp .env.example .env
# Edit .env if needed
```

### Step 2: Check Health
```bash
make health-check
```

### Step 3: Run
```bash
python main.py
```

**That's it!** Check `generated_projects/` for your created project and `logs/` for execution details.

## No Web UI?

Currently, the agent is **CLI-only**. If you want a web interface, you can:

1. **Use Docker** - Run via `docker-compose up` (better UX than CLI)
2. **Create REST API** - Wrap with FastAPI/Flask
3. **Build Dashboard** - Add real-time monitoring UI
4. **Use Logs** - View execution via log files

Would you like me to create a simple web UI/API for the agent?

## Support

- 📖 Full guide: [USER_GUIDE.md](USER_GUIDE.md)
- 🚀 Production guide: [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)
- 📋 Configuration: `.env.example`
- 📊 Logs: `logs/` directory
- 💾 Data: `state/memory.db` and `generated_projects/`
