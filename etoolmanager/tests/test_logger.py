# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/test_logger.py
# Purpose      : Unit tests for the logging configuration.
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

"""Tests for :mod:`etoolmanager.utils.logger`."""

from __future__ import annotations

import logging
from pathlib import Path

from etoolmanager.utils.logger import get_logger, setup_logging


class TestSetupLogging:
    """Tests for the logging configuration."""

    def test_setup_creates_handlers(self, tmp_path: Path) -> None:
        """setup_logging should attach console and file handlers."""
        log_file = tmp_path / "test.log"
        setup_logging(level=logging.DEBUG, log_file=log_file, console=False)

        root = logging.getLogger("etoolmanager")
        assert root.level == logging.DEBUG
        assert len(root.handlers) >= 1

        # The file handler should write to the requested path.
        logger = get_logger("test")
        logger.info("Hello from test")
        for handler in root.handlers:
            handler.flush()

        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "Hello from test" in content

    def test_setup_default_log_dir(self, tmp_path: Path, monkeypatch) -> None:
        """setup_logging without a log_file should create a timestamped file."""
        from etoolmanager.utils import logger as logger_module

        monkeypatch.setattr(logger_module, "LOG_DIR", tmp_path / "logs")
        setup_logging(level=logging.INFO, console=False)

        root = logging.getLogger("etoolmanager")
        assert len(root.handlers) >= 1

        # Find the file handler and verify the log dir was created.
        log_dir = tmp_path / "logs"
        assert log_dir.exists()
        files = list(log_dir.glob("etoolmanager_*.log"))
        assert len(files) >= 1

    def test_get_logger_returns_child(self) -> None:
        """get_logger should return a logger prefixed with etoolmanager."""
        logger = get_logger("mymodule")
        assert logger.name == "etoolmanager.mymodule"