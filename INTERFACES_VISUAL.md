# AutoDev Agent - Interfaces at a Glance

## 🎯 Quick Visual Guide

```
┌──────────────────────────────────────────────────────────────────┐
│              AutoDev Agent - Multiple Interfaces                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  1. 📟 CLI - Command Line                                        │
│     └─ python main.py                                            │
│        ↓                                                          │
│     Outputs logs to console + files                              │
│                                                                    │
│  2. ⚙️ CONFIG - Configuration File                               │
│     └─ .env (or .env.example as template)                        │
│        ↓                                                          │
│     Controls: complexity, retries, features, git, etc.           │
│                                                                    │
│  3. 📁 FILES - Generated Output                                  │
│     └─ generated_projects/[project-name]/                        │
│        ├─ app/ (source code)                                     │
│        ├─ tests/ (test files)                                    │
│        ├─ README.md                                              │
│        └─ validation_log.jsonl                                   │
│                                                                    │
│  4. 📊 LOGS - Execution History                                  │
│     └─ logs/                                                     │
│        ├─ autodev.log (main)                                     │
│        └─ errors.log (errors only)                               │
│                                                                    │
│  5. 🏥 HEALTH - Status Monitoring                                │
│     └─ make health-check                                         │
│        Database / Workspace / Disk check                         │
│                                                                    │
│  6. 💾 BACKUP - Data Protection                                  │
│     └─ make backup                                               │
│        state/backups/backup_*.db                                 │
│                                                                    │
│  7. 🐳 DOCKER - Container Interface                              │
│     └─ docker-compose up -d                                      │
│        View logs: docker-compose logs -f                         │
│                                                                    │
│  8. 🐍 PYTHON API - Programmatic Access                          │
│     └─ from app import AutoDevOrchestrator                       │
│        Use in your own code                                      │
│                                                                    │
│  9. 💾 DATABASE - Direct Query Tool                              │
│     └─ sqlite3 state/memory.db                                   │
│        SELECT * FROM projects;                                   │
│                                                                    │
│  10. 🔐 VALIDATION - Output Log                                  │
│      └─ generated_projects/*/validation_log.jsonl                │
│         JSON format check history                                │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

## 📍 Where Everything Is

```
AI-agent/
│
├─ main.py ........................... CLI Entry Point (Execute here)
│
├─ .env ............................. Configuration (Edit settings here)
├─ .env.example ..................... Configuration Template
│
├─ logs/ ............................ Log Files (Check results here)
│   ├─ autodev.log .................. Main execution log
│   ├─ errors.log ................... Errors only
│   └─ backup_*.md .................. Backup metadata
│
├─ generated_projects/ ............. Generated Output (View here)
│   ├─ habit-api/
│   │  ├─ app/main.py .............. Generated source code
│   │  ├─ README.md ................ Generated documentation
│   │  └─ validation_log.jsonl ..... Validation history
│   ├─ csv-inspector/
│   └─ log-summarizer/
│
├─ state/ ........................... Database & Locks
│   ├─ memory.db .................... SQLite database
│   ├─ scheduler.lock ............... Process lock
│   └─ backups/ ..................... Backup files
│
├─ Makefile ......................... Automation Commands
├─ docker-compose.yml ............... Container Setup
├─ Dockerfile ....................... Container Image
│
└─ docs/ ............................ Documentation
    ├─ USER_GUIDE.md ............... How to Use
    ├─ INTERFACE_GUIDE.md .......... This file
    ├─ PRODUCTION_GUIDE.md ......... Deployment
    └─ README.md ................... Overview
```

## 🚀 Fastest Way to Get Started

### Step 1: Configure (30 seconds)
```bash
cp .env.example .env
```

### Step 2: Check (10 seconds)
```bash
make health-check
```

### Step 3: Run (1-5 minutes)
```bash
python main.py
```

### Step 4: View Results
```bash
# See generated project
ls generated_projects/

# View logs
tail -f logs/autodev.log

# Check database
sqlite3 state/memory.db "SELECT * FROM projects;"
```

## 🎮 Common Tasks & Where to Do Them

| Task | Interface | Command |
|------|-----------|---------|
| **Run once** | CLI | `python main.py` |
| **Change complexity** | Config | Edit `.env` or `AUTODEV_MAX_COMPLEXITY=3 python main.py` |
| **View generated code** | Files | `cat generated_projects/[name]/app/main.py` |
| **Check logs** | Logs | `tail -f logs/autodev.log` |
| **System status** | Health | `make health-check` |
| **Backup database** | Backup | `make backup` |
| **Run via Docker** | Docker | `docker-compose up -d` |
| **Query projects** | Database | `python -c "from app.memory import ..."`  |
| **Schedule runs** | Shell | Add to crontab |
| **Use in code** | Python API | `from app.orchestrator import ...` |

## 📱 User Experience Flow

```
START
  │
  ├─→ Configure .env file (⚙️ CONFIG INTERFACE)
  │
  ├─→ Run `python main.py` (📟 CLI INTERFACE)
  │
  ├─→ Agent generates project
  │   └─→ Outputs to generated_projects/ (📁 FILES INTERFACE)
  │
  ├─→ Logs execution to logs/ (📊 LOGS INTERFACE)
  │
  ├─→ Stores in state/memory.db (💾 DATABASE)
  │
  ├─→ You can check:
  │   ├─ Health: `make health-check` (🏥 HEALTH)
  │   ├─ Results: View generated_projects/ (📁 FILES)
  │   ├─ History: View logs/ (📊 LOGS)
  │   └─ Backups: `make backup` (💾 BACKUP)
  │
  └─→ Done! Exit code 0 = success
```

## 🔍 Example: Full Workflow

```bash
# 1. Setup
cp .env.example .env         # Configure
make setup                   # Install dependencies

# 2. Check System
make health-check            # Should show "healthy"

# 3. Run Agent
python main.py               # Generates a project

# 4. View Results
ls generated_projects/       # See generated projects
tail -50 logs/autodev.log    # View execution log

# 5. Inspect Generated Code
cd generated_projects/habit-api
cat README.md               # Read documentation
cat app/main.py             # View generated code
python -m pytest tests/     # Run tests

# 6. Backup
cd /path/to/autodev
make backup                 # Create backup

# 7. Schedule (Optional)
crontab -e                  # Add to cron:
# 0 */4 * * * cd /path && python main.py
```

## 💡 Key Concepts

### No Web UI
- AutoDev Agent is **CLI-based** (command-line)
- All interaction is text-based
- Data stored as files and database

### Multiple Access Points
- You can use it different ways:
  - Direct: `python main.py`
  - Scheduled: crontab
  - Automated: GitHub Actions
  - Containerized: `docker-compose up`
  - Programmatic: `from app import ...`

### Everything is Inspectable
- Generated code: `generated_projects/`
- Execution logs: `logs/`
- Database: `state/memory.db` (SQLite)
- Backups: `state/backups/`

### Three Main Outputs
1. **Generated Projects** - Actual code files
2. **Logs** - What happened during execution
3. **Metadata** - Project history in database

## 🆘 Need Help?

| Question | Answer | Where |
|----------|--------|-------|
| How do I use this? | Read USER_GUIDE.md | [USER_GUIDE.md](USER_GUIDE.md) |
| What's the interface? | This file | [INTERFACE_GUIDE.md](INTERFACE_GUIDE.md) |
| How to deploy? | See PRODUCTION_GUIDE.md | [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md) |
| What features exist? | See BUILD_SUMMARY.md | [BUILD_SUMMARY.md](BUILD_SUMMARY.md) |
| Config options? | See .env.example | [.env.example](.env.example) |
| Check logs | View logs/ directory | `tail -f logs/autodev.log` |
| Debug errors | View logs/errors.log | `cat logs/errors.log` |

---

## ✅ Summary

**AutoDev Agent has NO graphical web UI.**  
Instead, it has **10 different interfaces** for different use cases:

1. **CLI** - Run via command line
2. **Config** - Configure via .env
3. **Files** - View generated projects
4. **Logs** - Monitor execution
5. **Health** - Check system status
6. **Backup** - Protect data
7. **Docker** - Run in containers
8. **Python API** - Use as library
9. **Database** - Query directly
10. **Shell** - Automate execution

**Choose the one that works for you!** 🎯
