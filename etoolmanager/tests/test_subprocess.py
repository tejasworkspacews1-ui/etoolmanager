# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/test_subprocess.py
# Purpose      : Unit tests for the subprocess runner utility.
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

"""Tests for :mod:`etoolmanager.utils.subprocess_runner`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from etoolmanager.utils.subprocess_runner import (
    CommandResult,
    command_exists,
    run_command,
    which,
)


class TestCommandResult:
    """Tests for the CommandResult dataclass."""

    def test_ok_property_success(self) -> None:
        """ok should be True for returncode 0."""
        result = CommandResult(returncode=0)
        assert result.ok is True

    def test_ok_property_failure(self) -> None:
        """ok should be False for non-zero returncode."""
        result = CommandResult(returncode=1)
        assert result.ok is False

    def test_string_representation(self) -> None:
        """String form should contain status and command."""
        result = CommandResult(returncode=0, command=["git", "--version"])
        text = str(result)
        assert "OK" in text
        assert "git" in text


class TestRunCommand:
    """Tests for the run_command function."""

    @patch("etoolmanager.utils.subprocess_runner.subprocess.run")
    def test_successful_command(self, mock_run: MagicMock) -> None:
        """A successful command should return a CommandResult."""
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "git version 2.43.0\n"
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc

        result = run_command(["git", "--version"])

        assert result.ok
        assert result.stdout == "git version 2.43.0"
        assert result.command == ["git", "--version"]

    @patch("etoolmanager.utils.subprocess_runner.subprocess.run")
    def test_failed_command(self, mock_run: MagicMock) -> None:
        """A failed command should return a non-ok result."""
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = ""
        mock_proc.stderr = "fatal: not a git repository"
        mock_run.return_value = mock_proc

        result = run_command(["git", "status"], check=False)

        assert not result.ok
        assert "fatal" in result.stderr

    @patch("etoolmanager.utils.subprocess_runner.subprocess.run")
    def test_check_raises_on_failure(self, mock_run: MagicMock) -> None:
        """check=True should raise RuntimeError on non-zero exit."""
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = ""
        mock_proc.stderr = "error"
        mock_run.return_value = mock_proc

        with pytest.raises(RuntimeError):
            run_command(["git", "status"], check=True)

    @patch("etoolmanager.utils.subprocess_runner.subprocess.run")
    def test_timeout_raises_runtime_error(self, mock_run: MagicMock) -> None:
        """A timeout should raise RuntimeError."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["sleep", "10"], timeout=1
        )

        with pytest.raises(RuntimeError):
            run_command(["sleep", "10"], timeout=1)

    @patch("etoolmanager.utils.subprocess_runner.subprocess.run")
    def test_file_not_found_propagates(self, mock_run: MagicMock) -> None:
        """FileNotFoundError should propagate to the caller."""
        mock_run.side_effect = FileNotFoundError("git")

        with pytest.raises(FileNotFoundError):
            run_command(["git", "--version"])


class TestWhichAndExists:
    """Tests for executable location helpers."""

    @patch("etoolmanager.utils.subprocess_runner.shutil.which")
    def test_which_found(self, mock_which: MagicMock) -> None:
        """which should return a Path when the executable exists."""
        import os

        mock_which.return_value = "/usr/bin/git"
        path = which("git")
        assert path is not None
        assert str(path) == str(os.path.normpath("/usr/bin/git"))

    @patch("etoolmanager.utils.subprocess_runner.shutil.which")
    def test_which_missing(self, mock_which: MagicMock) -> None:
        """which should return None when the executable is missing."""
        mock_which.return_value = None
        assert which("nonexistent") is None

    @patch("etoolmanager.utils.subprocess_runner.shutil.which")
    def test_command_exists_found(self, mock_which: MagicMock) -> None:
        """command_exists should return True when found."""
        mock_which.return_value = "/usr/bin/git"
        assert command_exists("git") is True

    @patch("etoolmanager.utils.subprocess_runner.shutil.which")
    def test_command_exists_missing(self, mock_which: MagicMock) -> None:
        """command_exists should return False when missing."""
        mock_which.return_value = None
        assert command_exists("git") is False