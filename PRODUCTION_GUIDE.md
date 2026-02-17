# AutoDev Agent - Production Deployment Guide

AutoDev Agent is an autonomous software engineering pipeline that generates, validates, and optionally publishes complete, tested projects.

## Features

### Core Capabilities
- **Autonomous Project Generation**: Creates complete, structured projects from concept to deployment
- **Validation Pipeline**: Comprehensive checks including syntax, linting, type-checking, and test coverage
- **Intelligent Correction**: Automatically fixes common linting and validation issues
- **Security Scanning**: Built-in policy enforcement for generated code
- **Memory & History**: SQLite-backed project tracking and execution history
- **Scheduler Lock**: Prevents concurrent execution with automatic stale lock recovery

### Production Features
- ✓ Structured JSON logging with rotating file handlers
- ✓ Health check system with detailed status reporting
- ✓ Database backup and recovery utilities
- ✓ Graceful shutdown with signal handling
- ✓ Docker containerization with health checks
- ✓ Comprehensive CI/CD pipeline (GitHub Actions)
- ✓ Security scanning and dependency management
- ✓ Error tracking and audit logging

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ AutoDev Agent Orchestrator                                  │
├─────────────────────────────────────────────────────────────┤
│ • Idea Generator      → Generate unique project concepts    │
│ • Planner             → Architecture design & planning      │
│ • Scaffolder          → Modular code generation             │
│ • Security Scanner    → Policy enforcement                  │
│ • Validator           → Multi-stage validation              │
│ • Correction Engine   → Smart error fixing                  │
│ • Git Workflow        → Feature branch automation           │
│ • GitHub Manager      → PR creation & management            │
└─────────────────────────────────────────────────────────────┘
                            ↓
         ┌──────────────────┴──────────────────┐
         ↓                                     ↓
   Memory Store (SQLite)             Scheduler Lock
   • Project History                 • Concurrency Control
   • Run Logs                         • Stale Recovery
   • Validation Reports              • Lock Cleanup
```

## Installation

### Development Setup

```bash
# Clone repository
git clone <repo-url>
cd AI-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v

# Run once
python main.py
```

### Docker Deployment

```bash
# Build image
docker build -t autodev-agent:latest .

# Run container
docker run -v $(pwd)/logs:/app/logs \
           -v $(pwd)/state:/app/state \
           -v $(pwd)/generated_projects:/app/generated_projects \
           -e AUTODEV_AUTO_GIT=false \
           autodev-agent:latest

# Using Docker Compose
docker-compose up -d
docker-compose logs -f autodev-agent
```

### Kubernetes Deployment

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: autodev-agent
spec:
  schedule: "0 */4 * * *"  # Every 4 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: autodev-agent
            image: ghcr.io/your-org/autodev-agent:latest
            env:
            - name: AUTODEV_MAX_RETRIES
              value: "3"
            - name: AUTODEV_MIN_COVERAGE
              value: "85"
            volumeMounts:
            - name: data
              mountPath: /app/state
          volumes:
          - name: data
            persistentVolumeClaim:
              claimName: autodev-data
          restartPolicy: OnFailure
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTODEV_MIN_COMPLEXITY` | 1 | Minimum project complexity (1-5) |
| `AUTODEV_MAX_COMPLEXITY` | 5 | Maximum project complexity (1-5) |
| `AUTODEV_MAX_RETRIES` | 3 | Validation retry attempts |
| `AUTODEV_MIN_COVERAGE` | 85 | Minimum test coverage percentage |
| `AUTODEV_RUN_LINT` | true | Enable flake8 linting |
| `AUTODEV_RUN_TYPECHECK` | false | Enable mypy type checking |
| `AUTODEV_RUN_COVERAGE` | true | Enforce test coverage |
| `AUTODEV_STRICT_VALIDATION` | true | Fail on any validation error |
| `AUTODEV_LOCK_STALE_SECONDS` | 3600 | Stale lock timeout (1 hour) |
| `AUTODEV_AUTO_GIT` | false | Enable git automation |
| `AUTODEV_AUTO_PR` | false | Enable PR creation |
| `AUTODEV_GITHUB_REPO` | "" | Target repository (owner/repo) |
| `GITHUB_TOKEN` | - | GitHub API token (required for PR) |

### Example Configuration Files

Create `.env` for local development:
```bash
AUTODEV_MIN_COMPLEXITY=2
AUTODEV_MAX_COMPLEXITY=4
AUTODEV_MAX_RETRIES=3
AUTODEV_RUN_LINT=true
AUTODEV_RUN_COVERAGE=true
AUTODEV_STRICT_VALIDATION=true
AUTODEV_AUTO_GIT=false
AUTODEV_AUTO_PR=false
```

## Operations

### Monitoring

Check system health:
```bash
python -c "
from app.health import HealthChecker
from app.config import AgentConfig
from pathlib import Path

config = AgentConfig()
checker = HealthChecker(config.memory_db_path, config.workspace_root)
health = checker.check()
print(f'Status: {health.status}')
print(f'Checks: {health.checks}')
"
```

### Logging

Logs are automatically collected in the `logs/` directory:
- `logs/autodev.log` - Main application log
- `logs/errors.log` - Error log only
- Rotating files with 10MB size limit, keeping 5 backups

### Database Backup & Recovery

```bash
python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig
from pathlib import Path

config = AgentConfig()
backup = DatabaseBackup(config.memory_db_path)

# Create backup
backup_path = backup.create_backup('Manual backup')
print(f'Backup created: {backup_path}')

# List backups
for backup_file, timestamp in backup.list_backups():
    print(f'{backup_file}: {timestamp}')

# Recover
backup.restore_backup(backup_path)

# Cleanup old backups
backup.cleanup_old_backups(keep_count=10)
"
```

### Project History

```bash
python -c "
from app.memory import MemoryStore
from app.config import AgentConfig

config = AgentConfig()
memory = MemoryStore(config.memory_db_path)

# List generated projects
projects = memory.list_project_names()
print(f'Generated projects: {projects}')
"
```

## CI/CD Pipeline

GitHub Actions workflow runs automatically on:
- Push to `main` or `develop`
- Pull requests
- Scheduled every 4 hours

Pipeline includes:
1. **Test Suite**: Unit tests with coverage reporting
2. **Linting**: Flake8 code quality checks
3. **Type Checking**: MyPy static type analysis
4. **Docker Build**: Build and push container image
5. **Security Scan**: Trivy vulnerability scanning
6. **Health Check**: System health validation

## Troubleshooting

### Exit Code 1 - Validation Failed
```bash
# Check latest validation logs
find generated_projects -name validation_log.jsonl -exec tail -1 {} \;

# Check system health
python -c "from app.health import HealthChecker; from app.config import AgentConfig; h = HealthChecker(AgentConfig().memory_db_path, AgentConfig().workspace_root); print(h.check())"
```

### Lock Acquisition Failed
```bash
# Check scheduler lock
ls -la state/scheduler.lock

# Force release (use with caution!)
rm state/scheduler.lock
```

### Database Errors
```bash
# Verify database integrity
python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig

backup = DatabaseBackup(AgentConfig().memory_db_path)
if backup.verify_database():
    print('Database OK')
else:
    print('Database corrupted - consider restoring from backup')
"
```

## Performance Tuning

### Memory Usage
- Database uses on-disk SQLite (minimal RAM)
- Project scaffolding done in memory (depends on project size)
- Cleanup generated_projects/ directory periodically

### CPU Usage
- Validation (linting, testing) is I/O bound
- Type checking (mypy) is CPU intensive
- Disable `AUTODEV_RUN_TYPECHECK` if CPU limited

### Scaling
- Use scheduler lock for distributed execution (prevents conflicts)
- Run multiple instances concurrently (each acquires/releases lock)
- Backup database regularly for disaster recovery

## Security Considerations

1. **Code Generation**
   - All generated code scanned against forbidden patterns
   - Security policy enforced before validation

2. **Git Integration**
   - Requires valid GitHub token for PR automation
   - Features branch per project (prevents overwriting)
   - Conventional commits for audit trail

3. **Database**
   - SQLite file should be protected from unauthorized access
   - Regular backups stored securely
   - Consider encryption for sensitive data

4. **Logging**
   - Logs contain project names and execution details
   - Rotate logs periodically
   - Sanitize before sharing

## Support & Contributing

For issues and feature requests, refer to the project repository.

## License

See LICENSE file for details.
