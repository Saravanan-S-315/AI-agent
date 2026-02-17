# AutoDev Agent - Web UI Guide

## 🌐 Overview

AutoDev Agent now has a **modern web-based user interface** where you can:

1. Configure project generation settings
2. Start tasks with one click
3. Monitor execution in real-time
4. View generated projects
5. Check system health
6. View execution logs

**No command-line knowledge required!**

## 🚀 Quick Start

### Step 1: Start the Web UI

```bash
python run_ui.py
```

**Output:**
```
======================================================================
🚀 AutoDev Agent - Web User Interface
======================================================================

📦 Checking dependencies...
✓ FastAPI, Uvicorn, Pydantic installed

⚙️  Loading application...
✓ Application loaded

======================================================================
🌐 Web Server Details:
   URL: http://localhost:8000
   API Docs: http://localhost:8000/docs
======================================================================

⏳ Starting server (opening browser in 2 seconds)...
✓ Browser opened

Server running... Press Ctrl+C to stop
```

### Step 2: Browser Opens Automatically

Your browser will open automatically to: **http://localhost:8000**

### Step 3: Configure Your Task

The UI shows:
- **Configuration Panel** (left) - Set task parameters
- **Status Panel** (right) - View system health
- **Logs** (bottom) - Real-time execution log
- **Projects** (bottom) - All generated projects

### Step 4: Start a Task

1. Adjust settings if needed:
   - **Min/Max Complexity** - How complex the project should be (1-5)
   - **Max Retries** - How many times to retry if validation fails
   - **Min Coverage** - Minimum test coverage percentage
   - **Feature Toggles** - Enable/disable linting, type checking, etc.

2. Click **▶ Start Task** button

3. Watch the logs update in real-time

4. Check status panel for health and results

5. View generated project in the **Projects** section

## 🎨 Web UI Features

### Configuration Panel (Left)

```
┌─────────────────────────┐
│ ⚙️ Task Configuration    │
├─────────────────────────┤
│ Minimum Complexity: 1   │ (1-5)
│ Maximum Complexity: 5   │ (1-5)
│ Max Retries: 3          │ (1-10)
│ Min Coverage: 85        │ (0-100%)
│ ☑ Enable Linting       │
│ ☑ Test Coverage        │
│ ☐ Type Checking        │
│ ☑ Strict Validation    │
│                        │
│ [▶ Start Task]         │
└─────────────────────────┘
```

### Status Panel (Right)

**Health Checks:**
- ✅ Database - OK
- ✅ Workspace - OK
- ✅ Disk Space - OK

**Execution Status:**
- Idle / Running (with spinner)

**Recent Activity:**
- Last timestamp and status

### Logs (Bottom)

Real-time colored logs:
- 🟢 **Green** - INFO/SUCCESS messages
- 🟡 **Yellow** - WARNING messages
- 🔴 **Red** - ERROR messages
- 🔵 **Blue** - CONFIG messages

### Projects Section (Bottom)

Shows all generated projects:
- Project name
- Category
- Complexity level
- Click to view details

## 📋 Configuration Options

### Complexity (1-5)

| Level | Description |
|-------|-------------|
| 1 | Very simple projects (CLI scripts) |
| 2 | Simple projects |
| 3 | Medium projects |
| 4 | Complex projects (APIs) |
| 5 | Very complex projects |

### Feature Toggles

| Toggle | Effect |
|--------|--------|
| **Linting** | Requires flake8 code quality checks |
| **Type Checking** | Requires mypy static type analysis (SLOW) |
| **Test Coverage** | Requires minimum % coverage |
| **Strict Validation** | Fail on any error vs. warning |

### Example Configurations

**Generate Many Simple Projects:**
```
Min Complexity: 1
Max Complexity: 2
Retries: 1
Coverage: 70%
Linting: ON
Type Check: OFF
```

**Generate Few Complex Projects:**
```
Min Complexity: 4
Max Complexity: 5
Retries: 5
Coverage: 90%
Linting: ON
Type Check: ON (slower)
```

## 🎮 Usage Workflow

### Scenario 1: Generate a Simple Project

1. **Configure:**
   - Min/Max Complexity: 1-3
   - Leave other settings default

2. **Start Task** → Click button

3. **Watch Logs:**
   - See project idea generation
   - Architecture planning
   - Code scaffolding
   - Validation progress

4. **View Result:**
   - Check "Generated Projects" section
   - Click project to see details
   - View auto-generated code

### Scenario 2: Generate Complex Project with High Coverage

1. **Configure:**
   - Min/Max Complexity: 4-5
   - Max Retries: 5 (more retries for complex)
   - Min Coverage: 90%
   - Enable: Linting + Type Checking (slower!)

2. **Start Task** → Click button

3. **Wait** (takes longer with type checking)

4. **Review Results:**
   - High-quality project generated
   - Full test coverage
   - Type-safe code

### Scenario 3: Batch Generation

1. **Configure for quick projects:**
   - Complexity: 1-2
   - Retries: 1
   - Linting: ON
   - Type Check: OFF

2. **Start multiple times:**
   - Generate one project at a time
   - Wait for "Ready" status between runs
   - Can't run tasks concurrently (lock prevents it)

## 📊 Understanding the Status Panel

### Health Status Indicators

**Healthy (Green):**
```
✅ All checks passing
All systems operational
```

**Degraded (Orange):**
```
⚠️ One check failing
Still operational, may have issues
```

**Unhealthy (Red):**
```
🔴 Multiple checks failing
Take action required
```

### Health Checks

- **Database** - SQLite database accessible
- **Workspace** - Can write to generated_projects/
- **Disk Space** - At least 100MB free

## 🔗 API Endpoints

The web UI uses these REST API endpoints:

```
GET  /api/health         # System health status
GET  /api/status         # Current execution status
POST /api/run            # Start new task
GET  /api/projects       # List all generated projects
GET  /api/project/{name} # Get project details
GET  /api/logs           # Application logs
POST /api/stop           # Stop running task
```

Interactive API docs available at: **http://localhost:8000/docs**

## 🛑 Stopping the Server

### Method 1: Keyboard Interrupt
```bash
Press Ctrl+C in terminal
```

Output:
```
======================================================================
✓ Server stopped cleanly
======================================================================
```

### Method 2: Close All Connections
- Close browser tab
- Wait for graceful shutdown

## 🔧 Troubleshooting

### "Port Already in Use"

```bash
# If port 8000 is in use:
# Option 1: Stop other server
# Option 2: Run on different port
python -m uvicorn app.web_ui:app --port 8001

# Then open: http://localhost:8001
```

### "Browser Won't Open"

Manually open in your browser: **http://localhost:8000**

### Task Won't Start

**Check:**
1. No task already running (wait for "Ready" status)
2. System health is "healthy"
3. Check logs for errors

**Restart:**
```bash
Ctrl+C to stop server
python run_ui.py to restart
```

### Logs Not Updating

**Refresh browser:** Press F5 or Cmd+R

The page auto-updates every 2 seconds, but manual refresh helps.

## 📱 Mobile Access

Access from another machine on same network:

```
Find your IP: ipconfig (Windows) or ifconfig (Mac/Linux)
Example: 192.168.1.100

Remote URL: http://192.168.1.100:8000
```

## 🔐 Security Notes

⚠️ **Important for Production:**

1. **No Authentication** - Anyone with URL can use
   - For development only
   - Add authentication for production

2. **No HTTPS** - HTTP only by default
   - Use reverse proxy (nginx) for HTTPS

3. **Local Network** - Bind to localhost only
   ```bash
   # Instead of 0.0.0.0, use:
   python -m uvicorn app.web_ui:app --host 127.0.0.1
   ```

## 📊 Advanced: Custom Configurations

### Start UI on Custom Port

```bash
python -c "
from app.web_ui import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=9000)
"
```

Then open: **http://localhost:9000**

### Automate UI with Scripts

```bash
# Start UI in background
nohup python run_ui.py > ui.log 2>&1 &

# Keep it running (screen/tmux)
tmux new-session -d -s autodev 'python run_ui.py'
tmux attach-session -t autodev
```

### API Integration Example

```python
import requests

# Start a task via API
response = requests.post('http://localhost:8000/api/run', json={
    "min_complexity": 1,
    "max_complexity": 5,
    "max_retries": 3,
    "min_coverage": 85,
    "run_lint": True
})

# Get status
status = requests.get('http://localhost:8000/api/status').json()
print(f"Running: {status['running']}")
```

## 🎯 Comparison: CLI vs Web UI

| Aspect | CLI | Web UI |
|--------|-----|--------|
| **Access** | Terminal only | Browser (anywhere) |
| **Ease** | Requires config knowledge | Intuitive UI |
| **Configuration** | `.env` file | Web forms |
| **Monitoring** | Tail logs | Real-time dashboard |
| **Projects** | File browsing | UI listing |
| **Automation** | Shell scripts | API calls |
| **Learning Curve** | Steep | Gentle |

## 📖 Related Documentation

- [USER_GUIDE.md](USER_GUIDE.md) - Complete feature guide
- [INTERFACE_GUIDE.md](INTERFACE_GUIDE.md) - All interfaces explained
- [INTERFACES_VISUAL.md](INTERFACES_VISUAL.md) - Visual guide

## ✅ Summary

**Web UI Workflow:**

1. Run `python run_ui.py`
2. Browser opens automatically
3. Configure settings (or use defaults)
4. Click "Start Task"
5. Watch logs update in real-time
6. View generated projects
7. Done! Press Ctrl+C to stop

**That's it! Simple and visual.** 🎉

---

**Need help?** Check the UI's built-in API docs: **http://localhost:8000/docs**
