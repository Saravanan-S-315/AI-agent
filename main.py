"""CLI entrypoint for AutoDev Agent."""

import argparse
import json
import os
import re
import signal
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.config import AgentConfig
from app.health import HealthChecker
from app.logging_config import configure_logging, get_logger
from app.orchestrator import AutoDevOrchestrator

logger = get_logger("main")
HISTORY_FILE = Path("state/cli_history.jsonl")

ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "blue": "\033[94m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "cyan": "\033[96m",
}

BLOCKED_TOKENS = (
    "rm -rf",
    "rmdir /s",
    "format ",
    "diskpart",
    "shutdown",
    "reboot",
    "del /f /s /q",
    "reg delete",
    "cipher /w",
)


@dataclass(slots=True)
class CommandPlan:
    """Executable command plan generated from a user task."""

    task: str
    commands: list[str]
    rationale: str
    risk: str = "low"


@dataclass(slots=True)
class CliSessionState:
    """Mutable state used by interactive CLI modes."""

    mode: str = "prompt"  # prompt | cmd
    auto_approve: bool = False
    dry_run: bool = False
    timeout_seconds: int = 600
    safe_mode: bool = True
    auto_git: bool | None = None
    auto_pr: bool | None = None
    use_llm: bool = True
    llm_model: str | None = None


def setup_signal_handlers() -> None:
    """Setup graceful shutdown handlers."""

    def signal_handler(signum: int, frame: object) -> None:
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def run_orchestrator_cycle(
    config: AgentConfig, *, auto_git: bool | None = None, auto_pr: bool | None = None
) -> int:
    """Run one autonomous development cycle."""
    if auto_git is not None:
        config.auto_git = auto_git
    if auto_pr is not None:
        config.auto_pr = auto_pr
    # Health check
    health_checker = HealthChecker(config.memory_db_path, config.workspace_root)
    health = health_checker.check()
    logger.info(f"Health status: {health.status}")
    if health.status == "unhealthy":
        logger.error(f"System unhealthy: {health.details}")
        return 1

    try:
        orchestrator = AutoDevOrchestrator(config)
        success = orchestrator.run_once()
        if success:
            logger.info("Orchestration cycle completed successfully")
            return 0
        else:
            logger.warning("Orchestration cycle failed validation")
            return 1
    except Exception as e:
        logger.error(f"Fatal error during orchestration: {type(e).__name__}: {e}", exc_info=True)
        return 1


def supports_color() -> bool:
    """Detect whether stdout supports ANSI colors."""
    return sys.stdout.isatty() and os.getenv("TERM") != "dumb"


def style(text: str, color: str | None = None, bold: bool = False) -> str:
    """Apply ANSI color styling when supported."""
    if not supports_color():
        return text

    parts: list[str] = []
    if bold:
        parts.append(ANSI["bold"])
    if color:
        parts.append(ANSI[color])
    parts.append(text)
    parts.append(ANSI["reset"])
    return "".join(parts)


def print_banner() -> None:
    """Render a compact startup banner."""
    print(style("AutoDev Agent CLI", color="cyan", bold=True))
    print(style("Modes: run | shell | prompt | cli", color="blue"))


def print_status(message: str, level: str = "info") -> None:
    """Print consistently formatted status lines."""
    colors = {"info": "blue", "ok": "green", "warn": "yellow", "err": "red"}
    markers = {"info": "[INFO]", "ok": "[OK]", "warn": "[WARN]", "err": "[ERR]"}
    print(style(f"{markers[level]} {message}", color=colors[level]))


def is_command_blocked(command: str) -> bool:
    """Block obviously destructive commands in safe mode."""
    normalized = command.strip().lower()
    return any(token in normalized for token in BLOCKED_TOKENS)


def append_history(
    *,
    task: str,
    command: str,
    exit_code: int,
    mode: str,
    dry_run: bool,
    skipped: bool = False,
) -> None:
    """Persist task execution history for observability."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "mode": mode,
        "task": task,
        "command": command,
        "exit_code": exit_code,
        "dry_run": dry_run,
        "skipped": skipped,
    }
    with HISTORY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def show_history(limit: int = 10) -> None:
    """Show most recent command history entries."""
    if not HISTORY_FILE.exists():
        print_status("No history yet.", level="warn")
        return

    lines = HISTORY_FILE.read_text(encoding="utf-8").strip().splitlines()
    recent = lines[-limit:]
    print(style(f"Recent {len(recent)} item(s):", color="cyan", bold=True))
    for line in recent:
        entry = json.loads(line)
        print(
            f"- {entry['timestamp']} | mode={entry['mode']} | exit={entry['exit_code']} | "
            f"cmd={entry['command']}"
        )


def render_plan(plan: CommandPlan) -> None:
    """Display plan before execution."""
    print(style("Execution Plan", color="cyan", bold=True))
    print(f"Task: {plan.task}")
    print(f"Rationale: {plan.rationale}")
    print(f"Risk: {plan.risk}")
    for index, cmd in enumerate(plan.commands, start=1):
        print(f"{index}. {cmd}")


def llm_plan(task: str, model: str | None = None) -> CommandPlan | None:
    """Use LLM to synthesize a command plan from an arbitrary task."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        import openai
    except ImportError:
        print_status("openai package not installed; cannot use LLM planning.", level="warn")
        return None

    client = openai.OpenAI(api_key=api_key)
    model_name = model or os.getenv("AUTODEV_LLM_MODEL", "gpt-4o-mini")
    system_prompt = (
        "You are a command-line planner. Return JSON with keys: commands (list of shell commands), "
        "rationale (short), risk (low|medium|high). Prefer safe commands; avoid destructive actions. "
        "Assume Windows PowerShell environment. Do not add explanations outside JSON."
    )
    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task},
            ],
            max_tokens=300,
        )
        content = resp.choices[0].message.content or ""
        json_text = None
        if content.strip().startswith("{"):
            json_text = content.strip()
        else:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                json_text = match.group(0)
        if not json_text:
            return None
        data = json.loads(json_text)
        commands = data.get("commands") or []
        if not isinstance(commands, list) or not commands:
            return None
        rationale = data.get("rationale", "LLM-generated plan")
        risk = data.get("risk", "medium")
        return CommandPlan(task=task, commands=commands, rationale=rationale, risk=risk)
    except Exception as exc:
        print_status(f"LLM planning failed: {exc}", level="warn")
        return None


def prompt_to_plan(task: str, *, use_llm: bool = True, llm_model: str | None = None) -> CommandPlan | None:
    """Convert natural-language prompt into executable command(s)."""
    normalized = task.strip().lower()
    if not normalized:
        return None

    if "run tests" in normalized or normalized == "test":
        return CommandPlan(task=task, commands=["py -3 -m pytest -q"], rationale="Run project test suite.")
    if "git status" in normalized or "repo status" in normalized:
        return CommandPlan(task=task, commands=["git status --short"], rationale="Inspect repository changes.")
    if "list files" in normalized or "show files" in normalized:
        return CommandPlan(task=task, commands=["dir"], rationale="List files in current directory.")
    if "current directory" in normalized or "where am i" in normalized:
        return CommandPlan(task=task, commands=["cd"], rationale="Show current working directory.")
    if "python version" in normalized:
        return CommandPlan(task=task, commands=["py -3 --version"], rationale="Print local Python version.")
    if "install dependencies" in normalized or "install requirements" in normalized:
        return CommandPlan(
            task=task,
            commands=["py -3 -m pip install -r requirements.txt"],
            rationale="Install project dependencies from requirements.txt.",
            risk="medium",
        )
    if "generate project" in normalized or "run agent" in normalized or "auto dev" in normalized:
        return CommandPlan(
            task=task,
            commands=["py -3 main.py run --auto-git"],
            rationale="Run AutoDev orchestration with git publishing enabled.",
            risk="medium",
        )
    if normalized.startswith("search for "):
        query = task[len("search for ") :].strip().strip("'\"")
        if query:
            return CommandPlan(
                task=task,
                commands=[f'rg -n \"{query}\" .'],
                rationale="Search repository text using ripgrep.",
            )
    if ("create text document" in normalized or "create file" in normalized) and "desktop" in normalized:
        return CommandPlan(
            task=task,
            commands=['echo Hello World > \"$env:USERPROFILE\\Desktop\\hello.txt\"'],
            rationale="Create hello.txt on desktop with Hello World content.",
            risk="low",
        )
    find_match = re.match(r"^find file (.+)$", normalized)
    if find_match:
        needle = find_match.group(1).strip().strip("'\"")
        if needle:
            return CommandPlan(
                task=task,
                commands=[f'rg --files | rg \"{needle}\"'],
                rationale="Find matching file names.",
            )
    if use_llm:
        return llm_plan(task, model=llm_model)

    return None


def run_shell_command(
    command: str,
    *,
    yes: bool = False,
    timeout_seconds: int = 600,
    safe_mode: bool = True,
    dry_run: bool = False,
    task_label: str | None = None,
    mode: str = "shell",
) -> int:
    """Run a local shell command with optional confirmation."""
    if safe_mode and is_command_blocked(command):
        print_status("Blocked potentially destructive command in safe mode.", level="err")
        append_history(
            task=task_label or command,
            command=command,
            exit_code=126,
            mode=mode,
            dry_run=dry_run,
            skipped=True,
        )
        return 126

    if not yes:
        confirmation = input(f"Run this command?\n  {command}\n[y/N]: ").strip().lower()
        if confirmation not in {"y", "yes"}:
            print_status("Cancelled by user.", level="warn")
            append_history(
                task=task_label or command,
                command=command,
                exit_code=1,
                mode=mode,
                dry_run=dry_run,
                skipped=True,
            )
            return 1

    if dry_run:
        print_status(f"DRY RUN: {command}", level="info")
        append_history(
            task=task_label or command,
            command=command,
            exit_code=0,
            mode=mode,
            dry_run=True,
        )
        return 0

    try:
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        print_status(f"Command timed out after {timeout_seconds} seconds.", level="err")
        append_history(
            task=task_label or command,
            command=command,
            exit_code=124,
            mode=mode,
            dry_run=dry_run,
        )
        return 124

    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)

    append_history(
        task=task_label or command,
        command=command,
        exit_code=completed.returncode,
        mode=mode,
        dry_run=dry_run,
    )
    return completed.returncode


def execute_plan(
    plan: CommandPlan,
    *,
    yes: bool,
    timeout_seconds: int,
    safe_mode: bool,
    dry_run: bool,
    mode: str,
) -> int:
    """Execute each command in a plan and stop on first failure."""
    render_plan(plan)
    last_exit = 0
    for command in plan.commands:
        last_exit = run_shell_command(
            command,
            yes=yes,
            timeout_seconds=timeout_seconds,
            safe_mode=safe_mode,
            dry_run=dry_run,
            task_label=plan.task,
            mode=mode,
        )
        if last_exit != 0:
            return last_exit
    return last_exit


def run_prompt_task(
    task: str,
    *,
    yes: bool = False,
    timeout_seconds: int = 600,
    safe_mode: bool = True,
    dry_run: bool = False,
    use_llm: bool = True,
    llm_model: str | None = None,
) -> int:
    """Run a natural-language task via prompt-to-plan translation."""
    plan = prompt_to_plan(task, use_llm=use_llm, llm_model=llm_model)
    if not plan:
        print_status("Could not map prompt to a safe command plan.", level="warn")
        print_status("Use `shell` mode for raw commands, or try `:help` patterns.", level="info")
        return 2

    return execute_plan(
        plan,
        yes=yes,
        timeout_seconds=timeout_seconds,
        safe_mode=safe_mode,
        dry_run=dry_run,
        mode="prompt",
    )


def print_cli_help() -> None:
    """Show interactive CLI commands."""
    print(style("Interactive Commands", color="cyan", bold=True))
    print(":help                  Show this help")
    print(":exit                  Quit")
    print(":run                   Run one AutoDev orchestration cycle")
    print(":health                Show health check")
    print(":history [n]           Show recent command history")
    print(":mode prompt|cmd       Switch task interpretation mode")
    print(":safe on|off           Toggle safe mode blocker")
    print(":dry on|off            Toggle dry-run mode")
    print("")
    print("Prompt examples:")
    print("- run tests")
    print("- list files")
    print("- search for scheduler")
    print("- find file main.py")


def print_health(config: AgentConfig) -> None:
    """Render health details in terminal."""
    health = HealthChecker(config.memory_db_path, config.workspace_root).check()
    level = "ok" if health.status == "healthy" else "warn"
    print_status(f"Health: {health.status}", level=level)
    for name, status in health.checks.items():
        item_level = "ok" if status == "ok" else "warn"
        print_status(f"{name}: {status}", level=item_level)


def run_interactive_cli(config: AgentConfig, state: CliSessionState) -> int:
    """Run an interactive CLI with prompt and command modes."""
    print_banner()
    print_status("Type tasks in plain English or use :mode cmd for raw commands.", level="info")
    print_status("Use :help for available commands.", level="info")

    while True:
        try:
            task = input(style("agent> ", color="cyan", bold=True)).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            return 0

        if not task:
            continue
        if task in {":exit", "exit", "quit"}:
            return 0
        if task == ":help":
            print_cli_help()
            continue
        if task == ":run":
            exit_code = run_orchestrator_cycle(
                config, auto_git=state.auto_git, auto_pr=state.auto_pr
            )
            print_status(f"Orchestrator exit code: {exit_code}", level="info")
            continue
        if task == ":health":
            print_health(config)
            continue
        if task.startswith(":history"):
            parts = task.split()
            limit = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
            show_history(limit=limit)
            continue
        if task.startswith(":mode "):
            new_mode = task.split(" ", 1)[1].strip().lower()
            if new_mode not in {"prompt", "cmd"}:
                print_status("Mode must be prompt or cmd.", level="warn")
            else:
                state.mode = new_mode
                print_status(f"Mode changed to {state.mode}.", level="ok")
            continue
        if task.startswith(":safe "):
            flag = task.split(" ", 1)[1].strip().lower()
            if flag in {"on", "off"}:
                state.safe_mode = flag == "on"
                print_status(f"Safe mode {'enabled' if state.safe_mode else 'disabled'}.", level="ok")
            else:
                print_status("Use :safe on|off", level="warn")
            continue
        if task.startswith(":dry "):
            flag = task.split(" ", 1)[1].strip().lower()
            if flag in {"on", "off"}:
                state.dry_run = flag == "on"
                print_status(f"Dry-run {'enabled' if state.dry_run else 'disabled'}.", level="ok")
            else:
                print_status("Use :dry on|off", level="warn")
            continue

        if state.mode == "cmd":
            exit_code = run_shell_command(
                task,
                yes=state.auto_approve,
                timeout_seconds=state.timeout_seconds,
                safe_mode=state.safe_mode,
                dry_run=state.dry_run,
                mode="cli-cmd",
            )
        else:
            exit_code = run_prompt_task(
                task,
                yes=state.auto_approve,
                timeout_seconds=state.timeout_seconds,
                safe_mode=state.safe_mode,
                dry_run=state.dry_run,
                use_llm=state.use_llm,
                llm_model=state.llm_model,
            )
        status_level = "ok" if exit_code == 0 else "warn"
        print_status(f"Exit code: {exit_code}", level=status_level)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="AutoDev Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run one AutoDev orchestration cycle")
    run_parser.add_argument("--auto-git", action="store_true", help="Enable git commit/branch publishing")
    run_parser.add_argument("--auto-pr", action="store_true", help="Enable PR creation (requires token)")

    shell_parser = subparsers.add_parser("shell", help="Run one shell command on this PC")
    shell_parser.add_argument("task", help="Shell command to run")
    shell_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    shell_parser.add_argument("--unsafe", action="store_true", help="Disable safe-mode command blocker")
    shell_parser.add_argument("--dry-run", action="store_true", help="Print command without running it")
    shell_parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds (default: 600)")

    prompt_parser = subparsers.add_parser("prompt", help="Run one natural-language task")
    prompt_parser.add_argument("task", help="Natural language task")
    prompt_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompts")
    prompt_parser.add_argument("--unsafe", action="store_true", help="Disable safe-mode command blocker")
    prompt_parser.add_argument("--dry-run", action="store_true", help="Print command plan without executing")
    prompt_parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds (default: 600)")
    prompt_parser.add_argument("--no-llm", action="store_true", help="Disable LLM planning fallback")
    prompt_parser.add_argument("--llm-model", type=str, help="Override LLM model name")

    cli_parser = subparsers.add_parser("cli", help="Interactive CLI with prompt + command modes")
    cli_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    cli_parser.add_argument("--mode", choices=("prompt", "cmd"), default="prompt", help="Initial input mode")
    cli_parser.add_argument("--unsafe", action="store_true", help="Disable safe-mode command blocker")
    cli_parser.add_argument("--dry-run", action="store_true", help="Print commands without running them")
    cli_parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds (default: 600)")
    cli_parser.add_argument("--auto-git", action="store_true", help="Enable git commit/branch publishing for :run")
    cli_parser.add_argument("--auto-pr", action="store_true", help="Enable PR creation for :run (requires token)")
    cli_parser.add_argument("--no-llm", action="store_true", help="Disable LLM planning fallback")
    cli_parser.add_argument("--llm-model", type=str, help="Override LLM model name")

    subparsers.add_parser("health", help="Print health status")
    history_parser = subparsers.add_parser("history", help="Show command history")
    history_parser.add_argument("--limit", type=int, default=20, help="Number of records to show")
    return parser


def main() -> int:
    """Run AutoDev in run/shell/interactive CLI modes."""
    config = AgentConfig.from_env()
    configure_logging(log_dir=Path("logs"))
    setup_signal_handlers()

    logger.info("AutoDev Agent starting...")
    logger.debug(f"Configuration: min_complexity={config.min_complexity}, max_complexity={config.max_complexity}")
    config.ensure_dirs()

    parser = build_parser()
    args = parser.parse_args()

    if args.command in (None, "run"):
        return run_orchestrator_cycle(
            config,
            auto_git=args.auto_git if hasattr(args, "auto_git") else None,
            auto_pr=args.auto_pr if hasattr(args, "auto_pr") else None,
        )

    if args.command == "shell":
        return run_shell_command(
            args.task,
            yes=args.yes,
            timeout_seconds=args.timeout,
            safe_mode=not args.unsafe,
            dry_run=args.dry_run,
            mode="shell",
        )

    if args.command == "prompt":
        return run_prompt_task(
            args.task,
            yes=args.yes,
            timeout_seconds=args.timeout,
            safe_mode=not args.unsafe,
            dry_run=args.dry_run,
            use_llm=not args.no_llm,
            llm_model=args.llm_model,
        )

    if args.command == "cli":
        state = CliSessionState(
            mode=args.mode,
            auto_approve=args.yes,
            dry_run=args.dry_run,
            timeout_seconds=args.timeout,
            safe_mode=not args.unsafe,
            auto_git=args.auto_git if hasattr(args, "auto_git") else None,
            auto_pr=args.auto_pr if hasattr(args, "auto_pr") else None,
            use_llm=not args.no_llm,
            llm_model=args.llm_model,
        )
        return run_interactive_cli(config, state)

    if args.command == "health":
        print_health(config)
        return 0

    if args.command == "history":
        show_history(limit=args.limit)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
