# AutoDev Agent

AutoDev Agent is a local autonomous engineering pipeline that generates project ideas, scaffolds code, validates quality gates, and stores run history.

## What This Repo Contains

- CLI workflows for `run`, `shell`, `prompt`, and interactive `cli` modes
- Optional LLM-assisted command planning for prompt/CLI modes
- Web UI (`FastAPI`) for triggering and monitoring runs
- Validation pipeline: syntax, lint, optional type-checking, optional coverage
- SQLite-backed project memory and run history
- Optional git/PR automation

## Quick Start

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
pytest -q
python main.py run
```

## Core Commands

```bash
# one orchestration cycle
python main.py run

# interactive terminal assistant
python main.py cli --mode prompt

# single shell command
python main.py shell "dir"

# single natural-language task
python main.py prompt "run tests"

# health and history
python main.py health
python main.py history --limit 20
```

## Web UI

```bash
python run_ui.py
```

Then open `http://localhost:8000` (API docs: `http://localhost:8000/docs`).

## Environment Variables

From `app/config.py`:

- `AUTODEV_MIN_COMPLEXITY` (default `1`)
- `AUTODEV_MAX_COMPLEXITY` (default `5`)
- `AUTODEV_MAX_RETRIES` (default `3`)
- `AUTODEV_MIN_COVERAGE` (default `85`)
- `AUTODEV_RUN_LINT` (default `true`)
- `AUTODEV_RUN_TYPECHECK` (default `false`)
- `AUTODEV_RUN_COVERAGE` (default `true`)
- `AUTODEV_STRICT_VALIDATION` (default `true`)
- `AUTODEV_LOCK_STALE_SECONDS` (default `3600`)
- `AUTODEV_AUTO_GIT` (default `false`)
- `AUTODEV_AUTO_PR` (default `false`)
- `AUTODEV_GITHUB_REPO` (default empty)
- `GITHUB_TOKEN` (required only for PR creation)

For LLM planning in `prompt` and `cli` modes:

- `OPENAI_API_KEY`
- `AUTODEV_LLM_MODEL` (default `gpt-4o-mini`)

## Documentation

- `PRODUCTION_GUIDE.md` for deployment and operations
- `DEPLOYMENT_CHECKLIST.md` for pre/post-deploy checks

## Unattended GitHub Contributions

The repository includes `.github/workflows/autodev.yml` to run the agent every 6 hours and on manual dispatch.
It also includes `.github/workflows/auto-merge.yml` to enable GitHub auto-merge for `feature/*` pull requests targeting `main`.

Required repository secrets:

- `OPENAI_API_KEY`
- `GH_TOKEN_PAT` (PAT with `repo` scope for PR creation; workflow falls back to `github.token` if unset)

Recommended branch protection on `main`:

- Require pull requests before merge
- Require status checks to pass
- Restrict direct pushes
- Enable auto-merge in repository settings

The workflow runs:

```bash
python main.py run --auto-git --auto-pr
```

Safety behavior:

- Includes health check before execution
- Retries failed runs up to 3 times
- Skips push/PR when no repository diff exists after staging

## Repository Layout

- `app/` core modules
- `tests/` test suite
- `main.py` CLI entrypoint
- `run_ui.py` Web UI launcher
- `.github/workflows/` CI workflows
