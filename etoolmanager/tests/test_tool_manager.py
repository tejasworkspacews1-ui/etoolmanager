# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/test_tool_manager.py
# Purpose      : Unit tests for the ToolManager facade.
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

"""Tests for :mod:`etoolmanager.core.tool_manager`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from etoolmanager.core.tool_manager import ToolManager, ToolStatus
from etoolmanager.utils.subprocess_runner import CommandResult


class TestToolManager:
    """Tests for the ToolManager facade."""

    def test_check_status_unknown_tool(self, sample_system) -> None:
        """Unknown tool names should raise ValueError."""
        manager = ToolManager(system=sample_system)
        with pytest.raises(ValueError):
            manager.check_status("nonexistent")

    @patch("etoolmanager.core.tool_manager.command_exists", return_value=True)
    @patch(
        "etoolmanager.core.tool_manager.run_command",
        return_value=CommandResult(
            returncode=0, stdout="git version 2.43.0", stderr=""
        ),
    )
    def test_check_status_installed(
        self, mock_run: MagicMock, mock_exists: MagicMock, sample_system
    ) -> None:
        """An installed tool should report installed=True with a version."""
        manager = ToolManager(system=sample_system)
        status = manager.check_status("git")

        assert status.installed is True
        assert status.version is not None
        assert status.version.major == 2
        assert status.meets_minimum is True

    @patch("etoolmanager.core.tool_manager.command_exists", return_value=False)
    def test_check_status_not_installed(
        self, mock_exists: MagicMock, sample_system
    ) -> None:
        """A missing tool should report installed=False."""
        manager = ToolManager(system=sample_system)
        status = manager.check_status("git")

        assert status.installed is False
        assert status.version is None
        assert status.meets_minimum is False

    @patch("etoolmanager.core.tool_manager.command_exists", return_value=True)
    @patch(
        "etoolmanager.core.tool_manager.run_command",
        return_value=CommandResult(
            returncode=0, stdout="git version 2.20.0", stderr=""
        ),
    )
    def test_check_status_below_minimum(
        self, mock_run: MagicMock, mock_exists: MagicMock, sample_system
    ) -> None:
        """A version below the minimum should report meets_minimum=False."""
        manager = ToolManager(system=sample_system)
        status = manager.check_status("git")

        assert status.installed is True
        assert status.meets_minimum is False

    @patch("etoolmanager.core.tool_manager.command_exists", return_value=True)
    @patch(
        "etoolmanager.core.tool_manager.run_command",
        return_value=CommandResult(returncode=1, stdout="", stderr="error"),
    )
    def test_check_status_version_failure(
        self, mock_run: MagicMock, mock_exists: MagicMock, sample_system
    ) -> None:
        """A failing version command should still report installed=True."""
        manager = ToolManager(system=sample_system)
        status = manager.check_status("git")

        assert status.installed is True
        assert status.version is None
        assert status.meets_minimum is False

    @patch("etoolmanager.core.tool_manager.command_exists", return_value=True)
    @patch(
        "etoolmanager.core.tool_manager.run_command",
        return_value=CommandResult(
            returncode=0, stdout="git version 2.43.0", stderr=""
        ),
    )
    def test_check_all_returns_statuses(
        self, mock_run: MagicMock, mock_exists: MagicMock, sample_system
    ) -> None:
        """check_all should return a status for every registered tool."""
        manager = ToolManager(system=sample_system)
        statuses = manager.check_all()

        assert len(statuses) >= 4
        names = {status.name for status in statuses}
        assert {"git", "python", "kicad", "ngspice"}.issubset(names)

    def test_install_unknown_tool(self, sample_system) -> None:
        """Installing an unknown tool should raise ValueError."""
        manager = ToolManager(system=sample_system)
        with pytest.raises(ValueError):
            manager.install("nonexistent")

    @patch(
        "etoolmanager.core.tool_manager.run_command",
        return_value=CommandResult(returncode=0, stdout="", stderr=""),
    )
    def test_install_uses_sudo_on_posix(
        self, mock_run: MagicMock, sample_system
    ) -> None:
        """Install on Ubuntu should prepend sudo."""
        manager = ToolManager(system=sample_system)
        result = manager.install("git")

        assert result.ok
        command = mock_run.call_args.args[0]
        assert command[0] == "sudo"
        assert "apt-get" in command

    @patch(
        "etoolmanager.core.tool_manager.run_command",
        return_value=CommandResult(returncode=0, stdout="", stderr=""),
    )
    def test_install_windows_no_sudo(
        self, mock_run: MagicMock, windows_system
    ) -> None:
        """Install on Windows should not prepend sudo."""
        manager = ToolManager(system=windows_system)
        result = manager.install("git")

        assert result.ok
        command = mock_run.call_args.args[0]
        assert command[0] == "winget"

    def test_uninstall_unknown_tool(self, sample_system) -> None:
        """Uninstalling an unknown tool should raise ValueError."""
        manager = ToolManager(system=sample_system)
        with pytest.raises(ValueError):
            manager.uninstall("nonexistent")

    @patch(
        "etoolmanager.core.tool_manager.run_command",
        return_value=CommandResult(returncode=0, stdout="", stderr=""),
    )
    def test_uninstall_uses_sudo_on_posix(
        self, mock_run: MagicMock, sample_system
    ) -> None:
        """Uninstall on Ubuntu should prepend sudo."""
        manager = ToolManager(system=sample_system)
        result = manager.uninstall("git")

        assert result.ok
        command = mock_run.call_args.args[0]
        assert command[0] == "sudo"
        assert "remove" in command


class TestToolStatus:
    """Tests for the ToolStatus dataclass."""

    def test_to_dict(self) -> None:
        """to_dict should return a plain dictionary."""
        status = ToolStatus(name="git", installed=True)
        data = status.to_dict()
        assert data["name"] == "git"
        assert data["installed"] is True
        assert data["version"] is None