# AutoDev Agent - User Guide

## What is AutoDev Agent?

AutoDev Agent is an **autonomous software engineering platform** that automatically generates, validates, and deploys complete, production-ready software projects. It's designed to handle the entire development lifecycle from concept to tested, deployable code.

## Core Features

### 🎯 Autonomous Project Generation
- **Idea Generation**: Creates unique project concepts based on configurable complexity levels
- **Architecture Planning**: Designs modular project structures with dependencies
- **Code Scaffolding**: Generates production-ready boilerplate code
- **Documentation**: Automatically creates comprehensive README files
- **Test Generation**: Creates test files with proper structure

### ✅ Comprehensive Validation
- **Syntax Checking**: Ensures all Python code is syntactically valid
- **Linting**: Runs flake8 to enforce code quality standards
- **Type Checking**: Optional mypy static type analysis
- **Test Coverage**: Validates minimum test coverage (default 85%)
- **Security Scanning**: Checks for forbidden patterns in code

### 🔧 Intelligent Correction
- **Auto-Fixes**: Automatically corrects common linting errors
- **Retry Logic**: Retries validation up to 3 times with corrections
- **Smart Recovery**: Applies targeted fixes based on validation errors

### 🔐 Production Features
- **Health Monitoring**: Real-time system health checks
- **Database Backups**: Automatic backup before each cycle
- **Structured Logging**: Detailed logs with rotating files
- **Error Tracking**: Separate error logs for alerting
- **Graceful Shutdown**: Signal handlers for clean termination

### 🚀 Deployment & Integration
- **Git Automation** (Optional): Creates feature branches and commits
- **GitHub PRs** (Optional): Automatically opens pull requests
- **Docker Support**: Containerized deployment ready
- **Kubernetes Ready**: CronJob configuration included
- **CI/CD Pipeline**: GitHub Actions workflow included

### 📊 Project Memory
- **SQLite Database**: Persistent project history
- **Run Tracking**: Records execution statistics
- **Idea Deduplication**: Prevents duplicate project generation
- **Performance Metrics**: Tracks retries and success rates

## How to Use

### 1. Basic Setup

```bash
# Clone repository
git clone <repo-url>
cd AI-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python validate_production.py
```

### 2. Run Once (Simple Execution)

```bash
# Generate one project
python main.py

# Expected output:
# [INFO] AutoDev Agent starting...
# [INFO] Health status: healthy
# [INFO] Generated project idea: [project-name]
# [INFO] Project scaffolded at: generated_projects/[project-name]
# [INFO] Validation passed
# [INFO] Orchestration cycle finished - success=True
```

### 3. Monitor Execution

```bash
# Check system health before running
python -c "
from app.health import HealthChecker
from app.config import AgentConfig
config = AgentConfig()
checker = HealthChecker(config.memory_db_path, config.workspace_root)
health = checker.check()
print(f'Status: {health.status}')
print(f'Checks: {health.checks}')
"

# View recent logs
tail -f logs/autodev.log

# Check errors
tail -f logs/errors.log
```

### 4. Manage Configuration

**Create `.env` file:**
```bash
cp .env.example .env
```

**Edit `.env` for your needs:**
```bash
# Project complexity (1-5)
AUTODEV_MIN_COMPLEXITY=2
AUTODEV_MAX_COMPLEXITY=4

# Validation settings
AUTODEV_MAX_RETRIES=3
AUTODEV_MIN_COVERAGE=85
AUTODEV_RUN_LINT=true
AUTODEV_RUN_COVERAGE=true

# Optional: Git automation
AUTODEV_AUTO_GIT=false
AUTODEV_AUTO_PR=false
```

## Usage Examples

### Example 1: Generate a Single Project

```bash
python main.py
```

**What happens:**
1. Agent acquires scheduler lock
2. Generates a new project idea
3. Plans architecture based on projct complexity
4. Scaffolds project files
5. Scans for security issues
6. Validates code (syntax, lint, coverage)
7. Auto-corrects any issues (up to 3 retries)
8. Stores project in history
9. Releases lock and exits

**Output location:** `generated_projects/[project-name]/`

### Example 2: Run with Docker

```bash
# Start services
docker-compose up -d

# Check status
docker-compose logs -f autodev-agent

# Stop services
docker-compose down
```

### Example 3: Run Tests

```bash
# Run test suite
make test

# Run with coverage report
pytest -v --cov=app --cov-report=html

# View HTML coverage report
open htmlcov/index.html
```

### Example 4: Code Quality Checks

```bash
# Lint code
make lint

# Type checking
make type-check

# Format code
make format

# All checks at once
make all
```

### Example 5: Database Management

```bash
# Create backup
make backup

# View backup history
python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig
b = DatabaseBackup(AgentConfig().memory_db_path)
for path, ts in b.list_backups()[:5]:
    print(f'{path}: {ts}')
"

# Restore from backup
python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig
b = DatabaseBackup(AgentConfig().memory_db_path)
b.restore_backup(<backup_path>)
"
```

### Example 6: View Generated Projects

```bash
# List all generated projects
python -c "
from app.memory import MemoryStore
from app.config import AgentConfig
m = MemoryStore(AgentConfig().memory_db_path)
projects = m.list_project_names()
print(f'Generated projects: {projects}')
"

# View project details
cd generated_projects/[project-name]
cat README.md
cat app/main.py
python -m pytest tests/
```

## Configuration Reference

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `AUTODEV_MIN_COMPLEXITY` | 1 | 1-5 | Minimum project complexity |
| `AUTODEV_MAX_COMPLEXITY` | 5 | 1-5 | Maximum project complexity |
| `AUTODEV_MAX_RETRIES` | 3 | 1-10 | Validation retry attempts |
| `AUTODEV_MIN_COVERAGE` | 85 | 0-100 | Minimum test coverage % |
| `AUTODEV_RUN_LINT` | true | true/false | Enable flake8 linting |
| `AUTODEV_RUN_TYPECHECK` | false | true/false | Enable mypy type checking |
| `AUTODEV_RUN_COVERAGE` | true | true/false | Require test coverage |
| `AUTODEV_STRICT_VALIDATION` | true | true/false | Fail on any error |
| `AUTODEV_LOCK_STALE_SECONDS` | 3600 | Seconds | Lock timeout |
| `AUTODEV_AUTO_GIT` | false | true/false | Create git commits |
| `AUTODEV_AUTO_PR` | false | true/false | Create GitHub PRs |
| `AUTODEV_GITHUB_REPO` | "" | owner/repo | GitHub repository |
| `GITHUB_TOKEN` | - | Token string | GitHub API token |

## Output Structure

### Generated Project Layout

```
generated_projects/[project-name]/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── models.py            # Data models
│   └── services.py          # Business logic
├── tests/
│   └── test_core.py         # Unit tests
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── pytest.ini               # Test configuration
└── validation_log.jsonl     # Validation history

```

### Validation Log Format

```json
{
  "attempt": 0,
  "success": false,
  "checks": {
    "syntax": true,
    "lint": false,
    "coverage": true
  },
  "logs": [
    "$ python -m compileall app",
    "Listing 'app'...",
    "$ flake8 app tests",
    "app/services.py:10:80: E501 line too long"
  ]
}
```

## Logs & Monitoring

### Log Files

- `logs/autodev.log` - Main application log (rotating, 10MB limit)
- `logs/errors.log` - Error events only
- `logs/` - Includes backup metadata

### Log Format

```
[2026-02-17 16:01:34] autodev.orchestrator - INFO - Generated project idea: habit-api
[2026-02-17 16:01:37] autodev.orchestrator - WARNING - Validation failed: {'syntax': True, 'lint': False}
[2026-02-17 16:01:39] autodev.orchestrator - INFO - Validation passed
```

### System Health

**Three status levels:**
- `healthy` - All checks passing
- `degraded` - One check failing
- `unhealthy` - Multiple checks failing

**Health checks:**
1. Database accessibility
2. Workspace directory writable
3. Disk space available (100MB minimum)

## Troubleshooting

### Issue: Exit code 1 (Validation Failed)

**Diagnosis:**
```bash
# Check latest validation logs
find generated_projects -name validation_log.jsonl -exec tail -1 {} \;

# Check health
make health-check
```

**Solution:**
```bash
# Adjust configuration to be less strict
AUTODEV_STRICT_VALIDATION=false python main.py

# Or increase retries
AUTODEV_MAX_RETRIES=5 python main.py
```

### Issue: Lock Acquisition Failed

**Diagnosis:**
```bash
ls -la state/scheduler.lock
```

**Solution:**
```bash
# Wait for lock timeout (1 hour default)
# Or force release (use carefully):
rm state/scheduler.lock
```

### Issue: Database Error

**Diagnosis:**
```bash
python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig
b = DatabaseBackup(AgentConfig().memory_db_path)
if b.verify_database():
    print('Database OK')
else:
    print('Database corrupted')
"
```

**Solution:**
```bash
# Restore from backup
make restore

# Or rollback to specific backup
python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig
b = DatabaseBackup(AgentConfig().memory_db_path)
for path, ts in b.list_backups()[:3]:
    print(f'{path}')
# Restore: b.restore_backup(<path>)
"
```

## Performance Tuning

### Reduce Execution Time
```bash
# Disable expensive checks
AUTODEV_RUN_TYPECHECK=false \
AUTODEV_RUN_LINT=false \
python main.py
```

### Reduce Resource Usage
```bash
# Lower complexity
AUTODEV_MAX_COMPLEXITY=2 python main.py

# Lower coverage requirement
AUTODEV_MIN_COVERAGE=70 python main.py
```

### Batch Processing
```bash
# Run multiple cycles
for i in {1..10}; do
    python main.py
    sleep 300  # 5 minute delay
done
```

## Development & Testing

### Run Full Test Suite
```bash
make test
```

### Run Tests with Coverage
```bash
pytest -v --cov=app --cov-report=html
open htmlcov/index.html
```

### Debug Mode
```bash
# Enable debug logging
python -c "
from app.logging_config import configure_logging
import logging
configure_logging(level=logging.DEBUG)
" && python main.py
```

### Test Individual Modules
```bash
pytest tests/test_orchestrator.py -v
pytest tests/test_validator.py -v
pytest tests/test_correction.py -v
```

## CI/CD Integration

### GitHub Actions

The project includes an automated workflow (`.github/workflows/ci-cd.yml`) that:

1. **Tests** - Runs pytest on every push/PR
2. **Linting** - Enforces code quality with flake8
3. **Type Checking** - Validates types with mypy
4. **Docker Build** - Builds and pushes container image
5. **Security Scan** - Runs Trivy vulnerability scanner
6. **Health Check** - Validates system health
7. **Scheduled** - Runs every 4 hours automatically

**View results:**
- GitHub Actions tab in repository
- Pull Request checks
- Commit status checks

## Deployment Options

### 1. Local Machine
```bash
python main.py
```

### 2. Docker Container
```bash
docker-compose up -d
docker-compose logs -f
```

### 3. Kubernetes Pod
```yaml
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: autodev
spec:
  schedule: "0 */4 * * *"  # Every 4 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: autodev
            image: ghcr.io/your-org/autodev-agent:latest
          restartPolicy: OnFailure
EOF
```

### 4. Cloud Functions
- Google Cloud Functions
- AWS Lambda
- Azure Functions

## API/Integration Examples

### Use Agent Programmatically

```python
from app.orchestrator import AutoDevOrchestrator
from app.config import AgentConfig

# Create instance
config = AgentConfig()
orchestrator = AutoDevOrchestrator(config)

# Run once
success = orchestrator.run_once()
print(f"Success: {success}")

# Check health
from app.health import HealthChecker
checker = HealthChecker(config.memory_db_path, config.workspace_root)
health = checker.check()
print(f"Status: {health.status}")

# Manage backups
from app.backup import DatabaseBackup
backup = DatabaseBackup(config.memory_db_path)
backup_path = backup.create_backup("manual")
print(f"Backup: {backup_path}")
```

### Query Project History

```python
from app.memory import MemoryStore
from app.config import AgentConfig

memory = MemoryStore(AgentConfig().memory_db_path)

# List all projects
projects = memory.list_project_names()
print(f"Projects: {projects}")

# Store new project (optional)
from app.models import ProjectCategory
memory.store_project("my-project", ProjectCategory.CLI, 3)
```

## Best Practices

### 1. **Regular Backups**
```bash
# Create weekly backup
0 2 * * 0 cd /path/to/autodev && python -c "
from app.backup import DatabaseBackup
from app.config import AgentConfig
DatabaseBackup(AgentConfig().memory_db_path).create_backup('weekly')
"
```

### 2. **Monitor Health**
```bash
# Add to cron job
*/15 * * * * make -C /path/to/autodev health-check >> health.log 2>&1
```

### 3. **Review Logs**
```bash
# Weekly log review
0 8 * * 1 tail -100 /path/to/autodev/logs/autodev.log | mail -s "AutoDev Weekly" admin@example.com
```

### 4. **Version Control**
```bash
# Track generated projects
git add generated_projects/
git commit -m "chore: add auto-generated projects"
git push
```

### 5. **Configuration Management**
```bash
# Use environment variables
export AUTODEV_MAX_COMPLEXITY=5
export AUTODEV_MIN_COVERAGE=90
python main.py
```

## Support & Resources

- [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md) - Deployment guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Pre-deployment checks
- [PRODUCTION_READY.md](PRODUCTION_READY.md) - Build details
- [BUILD_SUMMARY.md](BUILD_SUMMARY.md) - Feature summary
- Application logs in `logs/` directory

## FAQs

**Q: How often should I run the agent?**
A: Depends on your needs. Recommended: every 4 hours to 1 day. The GitHub Actions workflow runs every 4 hours.

**Q: Can multiple instances run simultaneously?**
A: No. The scheduler lock prevents concurrent execution. Use distributed lock manager for multiple machines.

**Q: What happens if validation fails?**
A: Agent auto-corrects issues up to 3 times (configurable). If still failing, project is discarded and error logged.

**Q: How much disk space is needed?**
A: ~1GB base + project size (~5-20MB each). Logs rotate, backups are configurable.

**Q: Can I customize generated projects?**
A: Currently, generation is deterministic based on configuration. Custom hooks could be added via extensions.

**Q: How do I integrate with GitHub?**
A: Set `AUTODEV_AUTO_GIT=true`, `AUTODEV_AUTO_PR=true`, and provide `GITHUB_TOKEN` via environment.

---

**Ready to start?** Run `python main.py` to generate your first project!
