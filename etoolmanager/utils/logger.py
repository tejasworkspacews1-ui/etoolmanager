# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/utils/logger.py
# Purpose      : Configure structured logging to console and file.
#
# Author       : Tejas Kamble
# Email        : tejasksocials@gmail.com
# Phone        : +91 8928545352
# Portfolio    : https://tejas-personal-portfolio-dev.vercel.app/
# LinkedIn     : https://www.linkedin.com/in/tejas-kamble-5342443b1
# GitHub       : https://github.com/tejasworkspacews1-ui
#
# Repository   : https://github.com/tejasworkspacews1-ui/etoolmanager
# Created      : 2026
#
# Developed by Tejas Kamble as a submission prototype for the
# FOSSEE eSim Semester Long Internship - Autumn 2026
# (Task 5: Automated Tool Manager).
# =============================================================================

"""Logging configuration for eToolManager.

This module sets up structured logging that writes to both the console
and a rotating file handler.  The ``get_logger`` function should be used
throughout the project so that all modules share the same handlers and
format, keeping the logs consistent and easy to debug.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Default directory where eToolManager writes its logs.
LOG_DIR: Path = Path(__file__).resolve().parent.parent.parent / "logs"

# Format used for every log record.  The ``%(levelname)s`` field is
# left-padded so that DEBUG / INFO / WARNING / ERROR line up nicely.
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_formatter() -> logging.Formatter:
    """Return the formatter used by all handlers.

    Returns:
        logging.Formatter: Configured with the standard log format.
    """
    return logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE_FORMAT)


def setup_logging(
    *,
    level: int = logging.INFO,
    log_file: Path | None = None,
    console: bool = True,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> None:
    """Configure the root logger used by every eToolManager module.

    Args:
        level: Minimum logging level (default ``logging.INFO``).
        log_file: Optional explicit path to the log file.  If omitted a
            timestamped file is created inside the project ``logs/`` dir.
        console: Whether to attach a stream handler to stdout.
        max_bytes: Maximum size of a single log file before rotation.
        backup_count: Number of rotated log files to retain.

    Returns:
        None: Configure the root logger in-place.
    """
    root = logging.getLogger("etoolmanager")
    root.setLevel(level)
    root.handlers.clear()

    fmt = _build_formatter()

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(fmt)
        root.addHandler(console_handler)

    # Choose the log file path.  When the caller does not provide one we
    # derive a timestamped name so multiple runs do not overwrite each other.
    resolved_log_file = log_file
    if resolved_log_file is None:
        log_dir = LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        resolved_log_file = log_dir / f"etoolmanager_{stamp}.log"

    file_handler = RotatingFileHandler(
        resolved_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger for the given module name.

    Args:
        name: Usually ``__name__`` of the calling module.

    Returns:
        logging.Logger: Logger whose records are prefixed with the module.
    """
    return logging.getLogger(f"etoolmanager.{name}")