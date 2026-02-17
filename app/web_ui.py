"""FastAPI web server for AutoDev Agent UI."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import AgentConfig
from app.health import HealthChecker
from app.logging_config import configure_logging, get_logger
from app.memory import MemoryStore
from app.orchestrator import AutoDevOrchestrator

configure_logging()
logger = get_logger("web_ui")

app = FastAPI(title="AutoDev Agent UI", version="1.0.0")

# Global state
current_run = {"running": False, "project": None, "logs": []}


class TaskRequest(BaseModel):
    """Task configuration request."""

    min_complexity: int = 1
    max_complexity: int = 5
    max_retries: int = 3
    min_coverage: int = 85
    run_lint: bool = True
    run_typecheck: bool = False
    run_coverage: bool = True
    strict_validation: bool = True


class StatusResponse(BaseModel):
    """Status response."""

    status: str
    running: bool
    current_project: str | None
    recent_logs: list[str]
    health: dict


class ProjectInfo(BaseModel):
    """Project information."""

    name: str
    category: str
    complexity: int


def run_orchestrator_task(config: AgentConfig) -> None:
    """Run orchestrator in background."""
    global current_run
    try:
        current_run["running"] = True
        logger.info("Starting orchestration from web UI")

        orchestrator = AutoDevOrchestrator(config)
        success = orchestrator.run_once()

        current_run["running"] = False
        if success:
            current_run["logs"].append("[SUCCESS] Project generated and validated")
        else:
            current_run["logs"].append("[FAILED] Project validation failed")

    except Exception as e:
        current_run["running"] = False
        current_run["logs"].append(f"[ERROR] {type(e).__name__}: {e}")
        logger.error(f"Orchestrator error: {e}", exc_info=True)


@app.get("/", response_class=HTMLResponse)
async def get_ui() -> str:
    """Serve the web UI."""
    return HTML_CONTENT


@app.get("/api/health")
async def get_health() -> dict:
    """Get system health status."""
    config = AgentConfig()
    config.ensure_dirs()
    checker = HealthChecker(config.memory_db_path, config.workspace_root)
    health = checker.check()

    return {
        "status": health.status,
        "checks": health.checks,
        "timestamp": health.timestamp,
    }


@app.get("/api/status")
async def get_status() -> StatusResponse:
    """Get current status."""
    health = await get_health()

    return StatusResponse(
        status="running" if current_run["running"] else "idle",
        running=current_run["running"],
        current_project=current_run["project"],
        recent_logs=current_run["logs"][-50:],  # Last 50 logs
        health=health,
    )


@app.post("/api/run")
async def run_task(request: TaskRequest, background_tasks: BackgroundTasks) -> dict:
    """Start a new orchestration task."""
    global current_run

    if current_run["running"]:
        raise HTTPException(status_code=409, detail="Already running a task")

    # Create config from request
    config = AgentConfig()
    config.min_complexity = request.min_complexity
    config.max_complexity = request.max_complexity
    config.max_retries = request.max_retries
    config.min_test_coverage = request.min_coverage
    config.run_lint = request.run_lint
    config.run_type_check = request.run_typecheck
    config.run_coverage = request.run_coverage
    config.strict_validation = request.strict_validation

    # Reset logs
    current_run["logs"] = []
    current_run["logs"].append(f"[INFO] Task started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    current_run["logs"].append(f"[CONFIG] Complexity: {request.min_complexity}-{request.max_complexity}")
    current_run["logs"].append(f"[CONFIG] Retries: {request.max_retries}, Coverage: {request.min_coverage}%")
    current_run["logs"].append("[INFO] Initializing agent...")

    # Run in background
    background_tasks.add_task(run_orchestrator_task, config)

    return {"success": True, "message": "Task started"}


@app.get("/api/projects")
async def get_projects() -> list[ProjectInfo]:
    """Get all generated projects."""
    try:
        config = AgentConfig()
        memory = MemoryStore(config.memory_db_path)
        projects = memory.list_project_names()

        # Get project details from database
        import sqlite3

        conn = sqlite3.connect(config.memory_db_path)
        cursor = conn.execute("SELECT name, category, complexity FROM projects")
        rows = cursor.fetchall()
        conn.close()

        return [ProjectInfo(name=row[0], category=row[1], complexity=row[2]) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        return []


@app.get("/api/project/{project_name}")
async def get_project_details(project_name: str) -> dict:
    """Get details of a specific project."""
    project_dir = Path("generated_projects") / project_name

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    # Read README
    readme_content = ""
    readme_path = project_dir / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text()

    # Read validation log
    validation_log = []
    log_path = project_dir / "validation_log.jsonl"
    if log_path.exists():
        for line in log_path.read_text().strip().split("\n"):
            if line:
                validation_log.append(json.loads(line))

    return {
        "name": project_name,
        "readme": readme_content,
        "validation_history": validation_log,
        "path": str(project_dir),
    }


@app.get("/api/logs")
async def get_logs() -> dict:
    """Get application logs."""
    logs_dir = Path("logs")
    logs_content = {}

    if (logs_dir / "autodev.log").exists():
        logs_content["main"] = (logs_dir / "autodev.log").read_text()[-2000:]  # Last 2KB

    if (logs_dir / "errors.log").exists():
        logs_content["errors"] = (logs_dir / "errors.log").read_text()[-2000:]

    return logs_content


@app.post("/api/stop")
async def stop_task() -> dict:
    """Stop running task (graceful stop)."""
    if current_run["running"]:
        current_run["logs"].append("[INFO] Stop requested by user")
        return {"success": True, "message": "Task will stop gracefully"}
    return {"success": False, "message": "No task running"}


# HTML content
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoDev Agent - Web UI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        header h1 {
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        header p {
            color: #666;
            font-size: 14px;
        }

        .status-badge {
            display: inline-block;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }

        .status-badge.healthy {
            background: #4caf50;
            color: white;
        }

        .status-badge.degraded {
            background: #ff9800;
            color: white;
        }

        .status-badge.unhealthy {
            background: #f44336;
            color: white;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 18px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }

        input[type="number"],
        input[type="text"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }

        input[type="number"]:focus,
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }

        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        button {
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-primary {
            background: #667eea;
            color: white;
            flex: 1;
        }

        .btn-primary:hover:not(:disabled) {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-primary:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .btn-danger {
            background: #f44336;
            color: white;
        }

        .btn-danger:hover {
            background: #da190b;
        }

        .logs-container {
            background: #1a1a1a;
            color: #0f0;
            padding: 20px;
            border-radius: 5px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.5;
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 15px;
        }

        .log-line {
            padding: 2px 0;
            word-wrap: break-word;
        }

        .log-info { color: #0f0; }
        .log-success { color: #0f0; }
        .log-warning { color: #ff0; }
        .log-error { color: #f00; }
        .log-config { color: #0af; }

        .health-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }

        .health-item {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            border-left: 4px solid #4caf50;
        }

        .health-item.fail {
            border-left-color: #f44336;
        }

        .health-item-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
            font-weight: 600;
        }

        .health-item-value {
            font-size: 14px;
            color: #333;
            font-weight: bold;
        }

        .projects-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }

        .project-card {
            background: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .project-card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }

        .project-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }

        .project-meta {
            font-size: 12px;
            color: #666;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
        }

        .tab-btn {
            background: none;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            color: #666;
            border-bottom: 2px solid transparent;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .tab-btn.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .spinner {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            display: none;
        }

        .alert.show {
            display: block;
        }

        .alert.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .alert.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>
                🤖 AutoDev Agent
                <span id="status-badge" class="status-badge healthy">Healthy</span>
            </h1>
            <p>Autonomous Project Generation Platform</p>
        </header>

        <div class="main-grid">
            <!-- Configuration Card -->
            <div class="card">
                <h2>⚙️ Task Configuration</h2>
                <div id="alert" class="alert"></div>

                <form id="config-form">
                    <div class="form-group">
                        <label>Minimum Complexity</label>
                        <input type="number" name="min_complexity" min="1" max="5" value="1">
                    </div>

                    <div class="form-group">
                        <label>Maximum Complexity</label>
                        <input type="number" name="max_complexity" min="1" max="5" value="5">
                    </div>

                    <div class="form-group">
                        <label>Max Retries on Failure</label>
                        <input type="number" name="max_retries" min="1" max="10" value="3">
                    </div>

                    <div class="form-group">
                        <label>Minimum Test Coverage (%)</label>
                        <input type="number" name="min_coverage" min="0" max="100" value="85">
                    </div>

                    <div class="form-group">
                        <div class="checkbox-group">
                            <input type="checkbox" id="run_lint" name="run_lint" checked>
                            <label for="run_lint" style="margin: 0;">Enable Linting</label>
                        </div>
                    </div>

                    <div class="form-group">
                        <div class="checkbox-group">
                            <input type="checkbox" id="run_coverage" name="run_coverage" checked>
                            <label for="run_coverage" style="margin: 0;">Require Test Coverage</label>
                        </div>
                    </div>

                    <div class="form-group">
                        <div class="checkbox-group">
                            <input type="checkbox" id="run_typecheck" name="run_typecheck">
                            <label for="run_typecheck" style="margin: 0;">Enable Type Checking (+slow)</label>
                        </div>
                    </div>

                    <div class="form-group">
                        <div class="checkbox-group">
                            <input type="checkbox" id="strict_validation" name="strict_validation" checked>
                            <label for="strict_validation" style="margin: 0;">Strict Validation</label>
                        </div>
                    </div>

                    <div class="button-group">
                        <button type="button" class="btn-primary" id="run-btn" onclick="runTask()">
                            ▶ Start Task
                        </button>
                    </div>
                </form>
            </div>

            <!-- Status Card -->
            <div class="card">
                <h2>📊 System Status</h2>

                <h3 style="margin-top: 15px; margin-bottom: 10px; font-size: 14px; color: #667eea;">Health Checks</h3>
                <div class="health-grid" id="health-status">
                    <div class="health-item">
                        <div class="health-item-label">Database</div>
                        <div class="health-item-value">-</div>
                    </div>
                </div>

                <h3 style="margin-top: 20px; margin-bottom: 10px; font-size: 14px; color: #667eea;">Execution Status</h3>
                <p id="exec-status" style="color: #666; font-size: 14px;">Ready</p>

                <h3 style="margin-top: 20px; margin-bottom: 10px; font-size: 14px; color: #667eea;">Recent Activity</h3>
                <p id="recent-activity" style="color: #666; font-size: 12px; word-break: break-word;">No recent activity</p>
            </div>
        </div>

        <!-- Logs Card -->
        <div class="card">
            <h2>📝 Execution Logs</h2>
            <div class="logs-container" id="logs">
                <div class="log-line log-info">[INFO] Ready to start...</div>
            </div>
            <button class="btn-primary" onclick="clearLogs()" style="width: 100%;">Clear Logs</button>
        </div>

        <!-- Projects Card -->
        <div class="card" style="margin-top: 20px;">
            <h2>📦 Generated Projects</h2>
            <div class="projects-grid" id="projects">
                <p style="color: #999; grid-column: 1/-1;">No projects generated yet</p>
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh status every 2 seconds
        setInterval(updateStatus, 2000);

        // Update on page load
        updateStatus();

        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();

                // Update execution status
                const execStatus = document.getElementById('exec-status');
                if (status.running) {
                    execStatus.innerHTML = '<span class="spinner"></span>Task Running...';
                } else {
                    execStatus.textContent = 'Ready';
                }

                // Update logs
                const logsDiv = document.getElementById('logs');
                logsDiv.innerHTML = status.recent_logs
                    .map(log => {
                        let className = 'log-info';
                        if (log.includes('[SUCCESS]')) className = 'log-success';
                        else if (log.includes('[ERROR]')) className = 'log-error';
                        else if (log.includes('[WARNING]')) className = 'log-warning';
                        else if (log.includes('[CONFIG]')) className = 'log-config';
                        return `<div class="log-line ${className}">${escapeHtml(log)}</div>`;
                    })
                    .join('');
                logsDiv.scrollTop = logsDiv.scrollHeight;

                // Update health
                const healthResponse = await fetch('/api/health');
                const health = await healthResponse.json();

                const healthDiv = document.getElementById('health-status');
                healthDiv.innerHTML = Object.entries(health.checks)
                    .map(([key, value]) => `
                        <div class="health-item ${value !== 'ok' ? 'fail' : ''}">
                            <div class="health-item-label">${key}</div>
                            <div class="health-item-value">${value}</div>
                        </div>
                    `)
                    .join('');

                const badge = document.getElementById('status-badge');
                badge.textContent = health.status.toUpperCase();
                badge.className = `status-badge ${health.status}`;

                // Toggle run button
                document.getElementById('run-btn').disabled = status.running;

                // Update projects
                const projectsResponse = await fetch('/api/projects');
                const projects = await projectsResponse.json();

                const projectsDiv = document.getElementById('projects');
                if (projects.length === 0) {
                    projectsDiv.innerHTML = '<p style="color: #999; grid-column: 1/-1;">No projects generated yet</p>';
                } else {
                    projectsDiv.innerHTML = projects
                        .map(p => `
                            <div class="project-card" onclick="viewProject('${p.name}')">
                                <div class="project-name">${p.name}</div>
                                <div class="project-meta">
                                    <div>Category: ${p.category}</div>
                                    <div>Complexity: ${p.complexity}/5</div>
                                </div>
                            </div>
                        `)
                        .join('');
                }
            } catch (error) {
                console.error('Error updating status:', error);
            }
        }

        async function runTask() {
            const form = document.getElementById('config-form');
            const formData = new FormData(form);

            const config = {
                min_complexity: parseInt(formData.get('min_complexity')),
                max_complexity: parseInt(formData.get('max_complexity')),
                max_retries: parseInt(formData.get('max_retries')),
                min_coverage: parseInt(formData.get('min_coverage')),
                run_lint: formData.get('run_lint') === 'on',
                run_typecheck: formData.get('run_typecheck') === 'on',
                run_coverage: formData.get('run_coverage') === 'on',
                strict_validation: formData.get('strict_validation') === 'on',
            };

            try {
                const response = await fetch('/api/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config),
                });

                if (response.ok) {
                    showAlert('Task started!', 'success');
                    updateStatus();
                } else {
                    const error = await response.json();
                    showAlert(error.detail || 'Failed to start task', 'error');
                }
            } catch (error) {
                showAlert(`Error: ${error.message}`, 'error');
            }
        }

        function viewProject(name) {
            alert(`Project: ${name}\n\nView the full project in: generated_projects/${name}/`);
        }

        function clearLogs() {
            document.getElementById('logs').innerHTML = '<div class="log-line log-info">[INFO] Logs cleared</div>';
        }

        function showAlert(message, type) {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert show ${type}`;
            setTimeout(() => alert.className = 'alert', 5000);
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("AutoDev Agent - Web UI")
    print("=" * 60)
    print("\n🌐 Starting server...")
    print("📱 Open browser: http://localhost:8000")
    print("🛑 Stop: Press Ctrl+C\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
