# AutoDev Agent 2.0

AutoDev Agent is an autonomous software engineering pipeline that turns product goals into validated pull requests using a disciplined branch-first workflow.

## Production-Ready Capabilities in This Repository

- Scheduled single-run orchestration with stale lock recovery
- Unique project idea generation with SQLite-backed memory
- Architecture planning with configurable constraints
- Deterministic modular code scaffolding engine
- Validation pipeline (syntax, lint, test coverage, optional type-checking)
- Deterministic correction engine for failed validation attempts
- Security policy scanner for generated source files
- Optional git automation (feature branch + conventional commit)
- Optional GitHub PR creation via API token
- CI quality gates (flake8 + pytest coverage + mypy)

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python main.py
```

## Environment Configuration

- `AUTODEV_MAX_RETRIES` (default: `3`)
- `AUTODEV_MIN_COVERAGE` (default: `85`)
- `AUTODEV_RUN_LINT` (`true`/`false`)
- `AUTODEV_RUN_TYPECHECK` (`true`/`false`)
- `AUTODEV_RUN_COVERAGE` (`true`/`false`)
- `AUTODEV_STRICT_VALIDATION` (`true`/`false`)
- `AUTODEV_LOCK_STALE_SECONDS` (default: `3600`)
- `AUTODEV_AUTO_GIT` (`true`/`false`)
- `AUTODEV_AUTO_PR` (`true`/`false`)
- `AUTODEV_GITHUB_REPO` (e.g. `owner/repo`)
- `GITHUB_TOKEN` (required when `AUTODEV_AUTO_PR=true`)

## Execution Flow

1. Acquire scheduler lock
2. Generate new project idea
3. Build architecture plan
4. Scaffold modular project files
5. Run security scan
6. Run validation checks
7. Apply correction strategy and retry on failure
8. Persist run history and release lock
9. Optionally commit on feature branch and open PR

## Repository Layout

- `app/` core modules
- `tests/` unit tests
- `main.py` one-shot runner
- `.github/workflows/ci.yml` CI quality gates
