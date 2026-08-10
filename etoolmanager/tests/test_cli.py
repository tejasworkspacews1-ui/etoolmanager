# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/test_cli.py
# Purpose      : Unit tests for the Typer CLI commands.
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

"""Tests for :mod:`etoolmanager.cli.app`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from etoolmanager.cli.app import app
from etoolmanager.core.tool_manager import ToolStatus
from etoolmanager.utils.subprocess_runner import CommandResult

runner = CliRunner()


class TestSystemCommand:
    """Tests for the ``system`` command."""

    def test_system_command_runs(self) -> None:
        """The system command should exit successfully."""
        result = runner.invoke(app, ["system"])
        assert result.exit_code == 0
        assert "eToolManager - System Information" in result.stdout


class TestStatusCommand:
    """Tests for the ``status`` command."""

    @patch(
        "etoolmanager.cli.app.ToolManager.check_status",
        return_value=ToolStatus(
            name="git",
            installed=True,
            version=None,
            minimum_version=None,
            meets_minimum=False,
        ),
    )
    def test_status_single_tool(self, mock_status: MagicMock) -> None:
        """Status for a single tool should render a table."""
        result = runner.invoke(app, ["status", "git"])
        assert result.exit_code == 0
        assert "git" in result.stdout

    @patch(
        "etoolmanager.cli.app.ToolManager.check_all",
        return_value=[
            ToolStatus(name="git", installed=True),
            ToolStatus(name="python", installed=False),
        ],
    )
    def test_status_all_tools(self, mock_all: MagicMock) -> None:
        """Status for all tools should render a table."""
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "git" in result.stdout
        assert "python" in result.stdout

    @patch(
        "etoolmanager.cli.app.ToolManager.check_status",
        side_effect=ValueError("Unknown tool: foo"),
    )
    def test_status_unknown_tool(self, mock_status: MagicMock) -> None:
        """Unknown tool should exit with code 1."""
        result = runner.invoke(app, ["status", "foo"])
        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestInstallCommand:
    """Tests for the ``install`` command."""

    @patch(
        "etoolmanager.cli.app.ToolManager.install",
        return_value=CommandResult(returncode=0, stdout="", stderr=""),
    )
    def test_install_success(self, mock_install: MagicMock) -> None:
        """Successful install should print a success message."""
        result = runner.invoke(app, ["install", "git"])
        assert result.exit_code == 0
        assert "Successfully installed git" in result.stdout

    @patch(
        "etoolmanager.cli.app.ToolManager.install",
        return_value=CommandResult(returncode=1, stdout="", stderr="failed"),
    )
    def test_install_failure(self, mock_install: MagicMock) -> None:
        """Failed install should exit with code 1."""
        result = runner.invoke(app, ["install", "git"])
        assert result.exit_code == 1
        assert "Install failed" in result.stdout

    @patch(
        "etoolmanager.cli.app.ToolManager.install",
        side_effect=RuntimeError("No install command"),
    )
    def test_install_error(self, mock_install: MagicMock) -> None:
        """RuntimeError should exit with code 1."""
        result = runner.invoke(app, ["install", "git"])
        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestUninstallCommand:
    """Tests for the ``uninstall`` command."""

    @patch(
        "etoolmanager.cli.app.ToolManager.uninstall",
        return_value=CommandResult(returncode=0, stdout="", stderr=""),
    )
    def test_uninstall_success(self, mock_uninstall: MagicMock) -> None:
        """Successful uninstall should print a success message."""
        result = runner.invoke(app, ["uninstall", "git"])
        assert result.exit_code == 0
        assert "Successfully uninstalled git" in result.stdout

    @patch(
        "etoolmanager.cli.app.ToolManager.uninstall",
        return_value=CommandResult(returncode=1, stdout="", stderr="failed"),
    )
    def test_uninstall_failure(self, mock_uninstall: MagicMock) -> None:
        """Failed uninstall should exit with code 1."""
        result = runner.invoke(app, ["uninstall", "git"])
        assert result.exit_code == 1
        assert "Uninstall failed" in result.stdout


class TestCheckCommand:
    """Tests for the ``check`` command."""

    @patch("etoolmanager.cli.app.DependencyScanner.scan")
    @patch("etoolmanager.cli.app.ToolManager.check_all")
    def test_check_runs(self, mock_all: MagicMock, mock_scan: MagicMock) -> None:
        """The check command should render a summary table."""
        from etoolmanager.core.os_detector import SystemInfo
        from etoolmanager.dependency.scanner import (
            DependencyCheck,
            DependencyReport,
        )

        mock_scan.return_value = DependencyReport(
            timestamp="2026-01-01T00:00:00",
            system=SystemInfo(
                os_name="ubuntu",
                os_display="Ubuntu 22.04",
                version="22.04",
                architecture="x86_64",
                package_manager="apt-get",
                python_version="3.11.9",
            ),
            checks=[
                DependencyCheck(
                    category="python_version",
                    name="Python version",
                    ok=True,
                    detail="Detected 3.11.9",
                ),
                DependencyCheck(
                    category="binary",
                    name="kicad",
                    ok=False,
                    detail="Not installed",
                    fix="Install kicad",
                ),
            ],
            missing=[
                DependencyCheck(
                    category="binary",
                    name="kicad",
                    ok=False,
                    detail="Not installed",
                    fix="Install kicad",
                ),
            ],
            fixes=["Install kicad"],
            ready=False,
        )
        mock_all.return_value = []

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        assert "Environment Readiness" in result.stdout
        assert "Python version" in result.stdout
        assert "kicad" in result.stdout
        assert "Suggested fixes" in result.stdout

    @patch("etoolmanager.cli.app.DependencyScanner.scan")
    @patch("etoolmanager.cli.app.ToolManager.check_all")
    def test_check_with_json(
        self, mock_all: MagicMock, mock_scan: MagicMock, tmp_path
    ) -> None:
        """The check command with --json should write report files."""
        from etoolmanager.core.os_detector import SystemInfo
        from etoolmanager.dependency.scanner import (
            DependencyCheck,
            DependencyReport,
        )

        mock_scan.return_value = DependencyReport(
            timestamp="2026-01-01T00:00:00",
            system=SystemInfo(
                os_name="ubuntu",
                os_display="Ubuntu 22.04",
                version="22.04",
                architecture="x86_64",
                package_manager="apt-get",
                python_version="3.11.9",
            ),
            checks=[DependencyCheck(category="a", name="x", ok=True)],
            ready=True,
        )
        mock_all.return_value = []

        result = runner.invoke(
            app, ["check", "--json", "--output", str(tmp_path)]
        )

        assert result.exit_code == 0
        assert (tmp_path / "report.json").exists()
        assert (tmp_path / "report.md").exists()


class TestDoctorCommand:
    """Tests for the ``doctor`` command."""

    @patch("etoolmanager.cli.app.DependencyScanner.scan")
    def test_doctor_runs(self, mock_scan: MagicMock) -> None:
        """The doctor command should run the check."""
        from etoolmanager.core.os_detector import SystemInfo
        from etoolmanager.dependency.scanner import (
            DependencyCheck,
            DependencyReport,
        )

        mock_scan.return_value = DependencyReport(
            timestamp="2026-01-01T00:00:00",
            system=SystemInfo(
                os_name="ubuntu",
                os_display="Ubuntu 22.04",
                version="22.04",
                architecture="x86_64",
                package_manager="apt-get",
                python_version="3.11.9",
            ),
            checks=[DependencyCheck(category="a", name="x", ok=True)],
            ready=True,
        )

        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "Environment is ready" in result.stdout