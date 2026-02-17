# AutoDev Agent 2.0

AutoDev Agent is an autonomous software engineering pipeline that turns product goals into validated pull requests using a disciplined branch-first workflow.

## Current Production-Ready Baseline

This repository now provides a hardened baseline suitable for production iteration:

- Scheduler lock with stale-lock recovery
- Deterministic idea generation with duplicate avoidance
- Architecture planning with modular constraints
- SQLite memory for project and run history
- Validation pipeline with syntax, lint, coverage, and optional type checks
- Retry loop with deterministic correction hook and per-attempt validation logs
- CI quality gates (lint + coverage threshold + mypy)

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python main.py
```

## Configuration (Environment Variables)

- `AUTODEV_MAX_RETRIES` (default: `3`)
- `AUTODEV_MIN_COVERAGE` (default: `85`)
- `AUTODEV_RUN_LINT` (`true`/`false`)
- `AUTODEV_RUN_TYPECHECK` (`true`/`false`)
- `AUTODEV_RUN_COVERAGE` (`true`/`false`)
- `AUTODEV_STRICT_VALIDATION` (`true`/`false`)
- `AUTODEV_LOCK_STALE_SECONDS` (default: `3600`)

## Repository Layout

- `app/` core modules
- `tests/` unit tests
- `main.py` one-shot runner

## Next milestones

- Integrate LLM-backed code generation adapters
- Add GitHub API PR creation + merge controller
- Add security scan stage (e.g., bandit/pip-audit)
- Add deployment adapters for app/package targets
