"""Production-grade logging configuration for AutoDev Agent."""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path


def configure_logging(log_dir: Path = Path("logs"), level: int = logging.INFO) -> None:
    """Configure structured logging with file and console handlers."""
    log_dir.mkdir(parents=True, exist_ok=True)

    # Setup root logger
    root_logger = logging.getLogger("autodev")
    root_logger.setLevel(level)
    root_logger.propagate = False

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Rotating file handler (logs rotate at 10MB, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "autodev.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Error file handler (separate errors)
    error_handler = logging.FileHandler(log_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)

    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    for handler in [file_handler, console_handler, error_handler]:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(f"autodev.{name}")
