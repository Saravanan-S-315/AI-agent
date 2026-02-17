"""Main orchestration pipeline for AutoDev Agent."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .backup import DatabaseBackup
from .codegen import ProjectScaffolder
from .config import AgentConfig
from .correction import CorrectionEngine
from .documentation import generate_readme
from .git_workflow import GitWorkflow
from .github_manager import GitHubManager
from .idea_generator import IdeaGenerator
from .logging_config import get_logger
from .memory import MemoryStore
from .models import RunRecord, ValidationResult
from .planner import ArchitecturePlanner
from .scheduler import SchedulerLock
from .security import SecurityPolicyError, SecurityScanner
from .validator import Validator

logger = get_logger("orchestrator")



class AutoDevOrchestrator:
    """Coordinates generation, validation, correction, and contribution workflow."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self.config.ensure_dirs()
        self.memory = MemoryStore(self.config.memory_db_path)
        self.idea_generator = IdeaGenerator()
        self.planner = ArchitecturePlanner()
        self.validator = Validator()
        self.scheduler = SchedulerLock(
            self.config.schedule_lock_file, stale_after_seconds=self.config.lock_stale_seconds
        )
        self.scaffolder = ProjectScaffolder()
        self.correction_engine = CorrectionEngine()
        self.security_scanner = SecurityScanner()

    def run_once(self) -> bool:
        """Execute one autonomous cycle with retry-aware logging and correction hooks."""
        if not self.scheduler.acquire():
            logger.info("Could not acquire scheduler lock - another instance may be running")
            return False

        logger.info("Starting orchestration cycle")
        started = datetime.now(tz=timezone.utc)
        retries = 0
        success = False
        project_name = "n/a"

        # Create database backup before starting
        try:
            backup = DatabaseBackup(self.config.memory_db_path)
            backup_path = backup.create_backup("Pre-cycle backup")
            logger.debug(f"Database backup created: {backup_path}")
            backup.cleanup_old_backups(keep_count=10)
        except Exception as e:
            logger.warning(f"Failed to create database backup: {e}")

        try:
            logger.debug("Generating project idea...")
            idea = self.idea_generator.generate(
                existing_names=self.memory.list_project_names(),
                min_complexity=self.config.min_complexity,
                max_complexity=self.config.max_complexity,
            )
            project_name = idea.name
            logger.info(f"Generated project idea: {project_name} (category: {idea.category.value}, complexity: {idea.complexity})")

            logger.debug("Creating architecture plan...")
            plan = self.planner.create_plan(idea, self.config)

            logger.debug("Scaffolding project...")
            generated = self.scaffolder.generate(
                workspace_root=self.config.workspace_root,
                idea=idea,
                plan=plan,
                readme_text=generate_readme(idea, plan),
                config=self.config,
            )
            project_root = generated.root
            logger.info(f"Project scaffolded at: {project_root}")

            logger.debug("Storing project in memory...")
            self.memory.store_project(idea.name, idea.category, idea.complexity)

            logger.debug("Running security scan...")
            try:
                self.security_scanner.scan(project_root)
                logger.info("Security scan passed")
            except SecurityPolicyError as e:
                logger.error(f"Security policy violation: {e}")
                return False

            while retries <= self.config.max_retries:
                logger.info(f"Running validation (attempt {retries + 1}/{self.config.max_retries + 1})...")
                validation = self.validator.run(
                    project_root,
                    run_lint=self.config.run_lint,
                    run_type_check=self.config.run_type_check,
                    run_coverage=self.config.run_coverage,
                    min_coverage=self.config.min_test_coverage,
                    strict_validation=self.config.strict_validation,
                )
                self._write_validation_log(project_root, retries, validation)

                if validation.success:
                    logger.info("Validation passed")
                    success = True
                    if self.config.auto_git:
                        logger.debug("Publishing changes...")
                        try:
                            self._publish_changes(project_name)
                            logger.info("Changes published successfully")
                        except Exception as e:
                            logger.error(f"Failed to publish changes: {e}")
                    break

                logger.warning(f"Validation failed: {validation.checks}")
                retries += 1
                if retries <= self.config.max_retries:
                    logger.info(f"Applying corrections and retrying...")
                    self.correction_engine.apply(project_root, validation)
                else:
                    logger.error("Max retries exceeded")

            return success

        except Exception as e:
            logger.error(f"Unexpected error during orchestration: {type(e).__name__}: {e}", exc_info=True)
            return False
        finally:
            finished = datetime.now(tz=timezone.utc)
            duration = (finished - started).total_seconds()
            logger.info(f"Orchestration cycle finished - success={success}, duration={duration:.1f}s, retries={retries}")

            self.memory.store_run(
                RunRecord(
                    started_at=started,
                    finished_at=finished,
                    project_name=project_name,
                    retries=retries,
                    success=success,
                )
            )
            self.scheduler.release()

    def _publish_changes(self, project_name: str) -> None:
        """Create branch/commit and optionally open a pull request."""
        repo_root = Path.cwd()
        git = GitWorkflow(repo_root)
        branch = git.create_or_checkout_feature_branch(project_name)
        git.commit_project(project_name)
        if not self.config.auto_pr:
            return
        manager = GitHubManager(self.config.github_repo)
        manager.create_pull_request(
            title=f"feat: add {project_name} with tests and documentation",
            body="Automated contribution generated by AutoDev Agent.",
            head=branch,
            base="main",
        )

    @staticmethod
    def _write_validation_log(project_root: Path, attempt: int, result: ValidationResult) -> None:
        log_file = project_root / "validation_log.jsonl"
        entry = {
            "attempt": attempt,
            "success": result.success,
            "checks": result.checks,
            "logs": result.logs,
        }
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
