# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/test_dependency.py
# Purpose      : Unit tests for the dependency scanner.
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

"""Tests for :mod:`etoolmanager.dependency.scanner`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from etoolmanager.core.tool_manager import ToolStatus
from etoolmanager.dependency.scanner import (
    DependencyCheck,
    DependencyReport,
    DependencyScanner,
    REQUIRED_PACKAGES,
)


class TestDependencyCheck:
    """Tests for the DependencyCheck dataclass."""

    def test_to_dict(self) -> None:
        """to_dict should return a plain dictionary."""
        check = DependencyCheck(
            category="binary", name="git", ok=True, detail="Installed: 2.43.0"
        )
        data = check.to_dict()
        assert data["category"] == "binary"
        assert data["name"] == "git"
        assert data["ok"] is True


class TestDependencyReport:
    """Tests for the DependencyReport dataclass."""

    def test_counts(self, sample_system) -> None:
        """passed_count and failed_count should be correct."""
        report = DependencyReport(
            timestamp="2026-01-01T00:00:00",
            system=sample_system,
            checks=[
                DependencyCheck(category="a", name="x", ok=True),
                DependencyCheck(category="b", name="y", ok=False),
                DependencyCheck(category="c", name="z", ok=True),
            ],
            missing=[
                DependencyCheck(category="b", name="y", ok=False),
            ],
            fixes=["Fix y"],
            ready=False,
        )
        assert report.passed_count == 2
        assert report.failed_count == 1

    def test_to_dict(self, sample_system) -> None:
        """to_dict should include summary and checks."""
        report = DependencyReport(
            timestamp="2026-01-01T00:00:00",
            system=sample_system,
            checks=[DependencyCheck(category="a", name="x", ok=True)],
            ready=True,
        )
        data = report.to_dict()
        assert data["ready"] is True
        assert data["summary"]["total"] == 1
        assert data["summary"]["passed"] == 1
        assert data["system"]["os_name"] == "ubuntu"


class TestDependencyScanner:
    """Tests for the DependencyScanner."""

    def test_scan_returns_report(self, sample_system) -> None:
        """scan should return a DependencyReport with all checks."""
        scanner = DependencyScanner(system=sample_system)
        report = scanner.scan()

        assert isinstance(report, DependencyReport)
        assert report.timestamp
        assert len(report.checks) > 0
        assert report.system.os_name == "ubuntu"

    @patch(
        "etoolmanager.dependency.scanner.command_exists",
        return_value=True,
    )
    def test_scan_pip_found(self, mock_exists: MagicMock, sample_system) -> None:
        """pip check should pass when pip is on PATH."""
        scanner = DependencyScanner(system=sample_system)
        report = scanner.scan()

        pip_check = next(
            (c for c in report.checks if c.category == "pip"), None
        )
        assert pip_check is not None
        assert pip_check.ok is True

    @patch(
        "etoolmanager.dependency.scanner.command_exists",
        return_value=False,
    )
    def test_scan_pip_missing(self, mock_exists: MagicMock, sample_system) -> None:
        """pip check should fail when pip is not on PATH."""
        scanner = DependencyScanner(system=sample_system)
        report = scanner.scan()

        pip_check = next(
            (c for c in report.checks if c.category == "pip"), None
        )
        assert pip_check is not None
        assert pip_check.ok is False
        assert pip_check.fix is not None

    def test_scan_python_version_check(self, sample_system) -> None:
        """Python version check should always be present."""
        scanner = DependencyScanner(system=sample_system)
        report = scanner.scan()

        py_check = next(
            (c for c in report.checks if c.category == "python_version"), None
        )
        assert py_check is not None
        assert py_check.name == "Python version"

    def test_scan_env_vars(self, sample_system) -> None:
        """Environment variable checks should be present."""
        scanner = DependencyScanner(system=sample_system)
        report = scanner.scan()

        env_checks = [c for c in report.checks if c.category == "env_var"]
        assert len(env_checks) >= 2

    def test_scan_packages(self, sample_system) -> None:
        """Package checks should cover all required packages."""
        scanner = DependencyScanner(system=sample_system)
        report = scanner.scan()

        package_checks = [c for c in report.checks if c.category == "package"]
        names = {c.name for c in package_checks}
        assert set(REQUIRED_PACKAGES).issubset(names)

    def test_scan_binaries(self, sample_system) -> None:
        """Binary checks should include kicad and ngspice."""
        scanner = DependencyScanner(system=sample_system)
        report = scanner.scan()

        binary_checks = [c for c in report.checks if c.category == "binary"]
        names = {c.name for c in binary_checks}
        assert {"kicad", "ngspice"}.issubset(names)

    def test_scan_ready_flag(self, sample_system) -> None:
        """ready should be True only when no checks fail."""
        scanner = DependencyScanner(system=sample_system)
        report = scanner.scan()

        assert report.ready == (len(report.missing) == 0)