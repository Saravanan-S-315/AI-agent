# 🚀 Quick Start - Web UI (30 seconds)

## Start the UI

```bash
python run_ui.py
```

✅ Browser opens automatically to **http://localhost:8000**

## What You'll See

```
┌──────────────────────────────────────────────────────┐
│                   AutoDev Agent                       │
├──────────────────┬──────────────────────────────────┤
│ Configuration    │ Status                           │
│ ┌──────────────┐ │ Health: ✅ Healthy             │
│ │Min Complexity│ │ Status: Ready                    │
│ │  [1 ────────━5] Project: None                     │
│ │Max Complexity│ │ Updated: Just now               │
│ │  [1 ────────━5] │                                 │
│ │Max Retries   │ │                                 │
│ │  [1 ────────10] │                                 │
│ │             │ │                                 │
│ │☑ Linting    │ │                                 │
│ │☑ Coverage   │ │                                 │
│ │☑ Type Check │ │                                 │
│ │             │ │                                 │
│ │[▶ Start Task]│ │                                 │
│ └──────────────┘ │                                 │
├──────────────────┴──────────────────────────────────┤
│ 📋 Logs (real-time)                                 │
│ [INFO] Starting orchestration...                    │
│ [INFO] Generating project idea...                   │
│ [SUCCESS] Generator complete                        │
├──────────────────────────────────────────────────────┤
│ 📦 Generated Projects                               │
│ • doc-qna-indexer (3/5 complexity)                  │
│ • api-rest-starter (2/5 complexity)                 │
└──────────────────────────────────────────────────────┘
```

## Use It

1. **Adjust settings** (or leave defaults)
2. **Click [▶ Start Task]**
3. **Watch logs update** in real-time
4. **See results** in Generated Projects section

## Stop It

```bash
Press Ctrl+C
```

## Common Tasks

### Generate Simple Project
- Min/Max Complexity: **1-3**
- Linting: **ON**
- Type Check: **OFF** (faster)
- Click **Start Task**

### Generate Complex Project
- Min/Max Complexity: **4-5**
- Max Retries: **5**
- Min Coverage: **90%**
- Type Check: **ON** (slower but better)
- Click **Start Task**

### Check System Health
- Look at **Status** panel (right side)
- Should show: ✅ Healthy

### View Logs
- Bottom section shows real-time logs
- Green = success, Red = error, Yellow = warning

### Access API Docs
- Go to: **http://localhost:8000/docs**

## API Endpoints

```
GET  /api/health    → System health
GET  /api/status    → Current status
POST /api/run       → Start task
GET  /api/projects  → List all projects
GET  /api/logs      → View logs
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8000 in use | Change port: `uvicorn app.web_ui:app --port 8001` |
| Browser won't open | Open manually: http://localhost:8000 |
| Task won't start | Wait for "Ready" status |
| Logs not updating | Refresh browser (F5) |

## Full Guides

- 📖 [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) - Complete guide
- 📖 [USER_GUIDE.md](USER_GUIDE.md) - All features
- 📖 [INTERFACE_GUIDE.md](INTERFACE_GUIDE.md) - All interfaces

---

**That's it!** You now have a modern web UI for AutoDev Agent. 🎉
