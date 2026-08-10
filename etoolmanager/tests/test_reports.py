# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/test_reports.py
# Purpose      : Unit tests for report generation (JSON and Markdown).
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

"""Tests for :mod:`etoolmanager.reports.generator`."""

from __future__ import annotations

import json
from pathlib import Path

from etoolmanager.core.tool_manager import ToolStatus
from etoolmanager.dependency.scanner import DependencyCheck, DependencyReport
from etoolmanager.reports.generator import (
    generate_json_report,
    generate_markdown_report,
)


def _make_report(sample_system) -> DependencyReport:
    """Build a deterministic DependencyReport for tests."""
    return DependencyReport(
        timestamp="2026-01-01T00:00:00",
        system=sample_system,
        checks=[
            DependencyCheck(
                category="python_version",
                name="Python version",
                ok=True,
                detail="Detected 3.11.9, required >= 3.8.0",
            ),
            DependencyCheck(
                category="binary",
                name="kicad",
                ok=False,
                detail="Not installed",
                fix="Install the kicad package using your package manager",
            ),
        ],
        missing=[
            DependencyCheck(
                category="binary",
                name="kicad",
                ok=False,
                detail="Not installed",
                fix="Install the kicad package using your package manager",
            ),
        ],
        fixes=["Install the kicad package using your package manager"],
        ready=False,
    )


class TestGenerateJsonReport:
    """Tests for JSON report generation."""

    def test_writes_valid_json(self, sample_system, tmp_report_dir: Path) -> None:
        """The JSON report should be valid and contain expected fields."""
        report = _make_report(sample_system)
        output = tmp_report_dir / "report.json"

        result = generate_json_report(report, output)

        assert result == output
        assert output.exists()

        data = json.loads(output.read_text(encoding="utf-8"))
        assert data["timestamp"] == "2026-01-01T00:00:00"
        assert data["ready"] is False
        assert data["system"]["os_name"] == "ubuntu"
        assert data["summary"]["total"] == 2
        assert data["summary"]["failed"] == 1
        assert len(data["checks"]) == 2
        assert len(data["missing"]) == 1
        assert len(data["suggested_fixes"]) == 1
        assert "author" in data
        assert data["author"]["name"] == "Tejas Kamble"

    def test_includes_tool_statuses(
        self, sample_system, tmp_report_dir: Path
    ) -> None:
        """Tool statuses should be included when provided."""
        report = _make_report(sample_system)
        statuses = [ToolStatus(name="git", installed=True)]
        output = tmp_report_dir / "report.json"

        generate_json_report(report, output, tool_statuses=statuses)

        data = json.loads(output.read_text(encoding="utf-8"))
        assert "tools" in data
        assert data["tools"][0]["name"] == "git"
        assert data["tools"][0]["installed"] is True

    def test_creates_parent_directories(
        self, sample_system, tmp_path: Path
    ) -> None:
        """Parent directories should be created automatically."""
        report = _make_report(sample_system)
        output = tmp_path / "nested" / "deep" / "report.json"

        generate_json_report(report, output)

        assert output.exists()


class TestGenerateMarkdownReport:
    """Tests for Markdown report generation."""

    def test_writes_markdown(self, sample_system, tmp_report_dir: Path) -> None:
        """The Markdown report should contain key sections."""
        report = _make_report(sample_system)
        output = tmp_report_dir / "report.md"

        result = generate_markdown_report(report, output)

        assert result == output
        assert output.exists()

        content = output.read_text(encoding="utf-8")
        assert "# eToolManager - Environment Readiness Report" in content
        assert "## System Information" in content
        assert "## Summary" in content
        assert "## Dependency Checks" in content
        assert "## Missing Dependencies" in content
        assert "## Suggested Fixes" in content
        assert "## Author & Attribution" in content
        assert "Tejas Kamble" in content
        assert "kicad" in content

    def test_includes_tool_table(
        self, sample_system, tmp_report_dir: Path
    ) -> None:
        """Tool statuses should render as a Markdown table."""
        report = _make_report(sample_system)
        statuses = [ToolStatus(name="git", installed=True)]
        output = tmp_report_dir / "report.md"

        generate_markdown_report(report, output, tool_statuses=statuses)

        content = output.read_text(encoding="utf-8")
        assert "## Installed Tools" in content
        assert "| Tool | Installed | Version | Minimum | Meets Minimum |" in content
        assert "| git | Yes |" in content

    def test_ready_report(self, sample_system, tmp_report_dir: Path) -> None:
        """A ready report should say no fixes are needed."""
        report = DependencyReport(
            timestamp="2026-01-01T00:00:00",
            system=sample_system,
            checks=[DependencyCheck(category="a", name="x", ok=True)],
            ready=True,
        )
        output = tmp_report_dir / "report.md"

        generate_markdown_report(report, output)

        content = output.read_text(encoding="utf-8")
        assert "No missing dependencies detected" in content
        assert "No fixes needed" in content