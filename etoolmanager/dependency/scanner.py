# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/dependency/scanner.py
# Purpose      : Scan the environment for missing eSim dependencies.
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

"""Dependency scanning for the eSim environment.

The :class:`DependencyScanner` checks the four categories declared in the
task specification:

* Python version
* ``pip`` availability
* Git binary
* required Python packages
* environment variables
* missing binaries

Every check produces a :class:`DependencyCheck` record, and the scanner
aggregates them into a :class:`DependencyReport` with suggested fixes and
an overall readiness flag.
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import os
import platform
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from etoolmanager.config.loader import get_tool
from etoolmanager.core.os_detector import SystemInfo, detect_system
from etoolmanager.core.tool_manager import ToolManager, ToolStatus
from etoolmanager.utils.logger import get_logger
from etoolmanager.utils.subprocess_runner import command_exists, run_command
from etoolmanager.utils.version import Version, parse_version

logger = get_logger(__name__)

# Python version required by eSim (3.8+ is realistic for the current eSim).
REQUIRED_PYTHON = Version(major=3, minor=8, patch=0)

# Python packages eSim relies on at runtime.
REQUIRED_PACKAGES: list[str] = [
    "numpy",
    "scipy",
    "matplotlib",
    "PyQt5",
    "kiwisolver",
    "sympy",
    "requests",
]

# Environment variables eSim expects to be set.
REQUIRED_ENV_VARS: list[str] = [
    "PATH",
    "HOME",
]

# Suggested fix templates keyed by check type.
_FIX_TEMPLATES: dict[str, str] = {
    "python_version": "Upgrade Python to at least 3.8 (recommended: 3.11+)",
    "pip": "Install pip using: python -m ensurepip --upgrade",
    "git": "Install Git: run 'etoolmanager install git'",
    "package": "Install Python package using: pip install {package}",
    "env_var": "Set the environment variable {var}",
    "binary": "Install the {binary} package using your package manager",
}


@dataclass
class DependencyCheck:
    """Result of a single dependency check.

    Attributes:
        category: Check category (``python_version``, ``binary``, ...).
        name: Display name of the dependency.
        ok: Whether the dependency is satisfied.
        detail: Human-readable detail of the result.
        fix: Suggested fix when the dependency is missing.
    """

    category: str
    name: str
    ok: bool = False
    detail: str = ""
    fix: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the check as a plain dictionary for reports."""
        return {
            "category": self.category,
            "name": self.name,
            "ok": self.ok,
            "detail": self.detail,
            "fix": self.fix,
        }


@dataclass
class DependencyReport:
    """Complete environment readiness report.

    Attributes:
        timestamp: When the scan was run (ISO 8601).
        system: Detected system information.
        checks: Individual dependency check results.
        missing: Only the failed checks.
        fixes: Unique suggested fixes for missing dependencies.
        ready: Whether all checks passed.
    """

    timestamp: str
    system: SystemInfo
    checks: list[DependencyCheck] = field(default_factory=list)
    missing: list[DependencyCheck] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)
    ready: bool = False

    @property
    def passed_count(self) -> int:
        """Number of checks that passed."""
        return sum(1 for check in self.checks if check.ok)

    @property
    def failed_count(self) -> int:
        """Number of checks that failed."""
        return len(self.missing)

    def to_dict(self) -> dict[str, Any]:
        """Return the report as a plain dictionary for JSON export."""
        return {
            "timestamp": self.timestamp,
            "system": self.system.to_dict(),
            "ready": self.ready,
            "summary": {
                "total": len(self.checks),
                "passed": self.passed_count,
                "failed": self.failed_count,
            },
            "checks": [check.to_dict() for check in self.checks],
            "missing": [check.to_dict() for check in self.missing],
            "suggested_fixes": self.fixes,
        }


class DependencyScanner:
    """Scan the environment against the eSim dependency checklist.

    Attributes:
        system: Detected system info.
        tool_manager: Shared tool manager for binary detection.
    """

    def __init__(
        self,
        system: SystemInfo | None = None,
        tool_manager: ToolManager | None = None,
    ) -> None:
        """Initialise the scanner.

        Args:
            system: Pre-detected system info (auto-detected if omitted).
            tool_manager: Optional shared tool manager.
        """
        self.system = system or detect_system()
        self.tool_manager = tool_manager or ToolManager(self.system)

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------
    def _check_python_version(self) -> DependencyCheck:
        """Verify the running Python version meets the minimum."""
        current = parse_version(platform.python_version())
        ok = bool(current and current >= REQUIRED_PYTHON)
        return DependencyCheck(
            category="python_version",
            name="Python version",
            ok=ok,
            detail=f"Detected {platform.python_version()}, required >= {REQUIRED_PYTHON}",
            fix=None if ok else _FIX_TEMPLATES["python_version"],
        )

    def _check_pip(self) -> DependencyCheck:
        """Verify pip is installed."""
        ok = command_exists("pip") or command_exists("pip3")
        detail = "pip found on PATH" if ok else "pip not found on PATH"
        return DependencyCheck(
            category="pip",
            name="pip",
            ok=ok,
            detail=detail,
            fix=None if ok else _FIX_TEMPLATES["pip"],
        )

    def _check_git(self) -> DependencyCheck:
        """Verify Git is installed."""
        status = self.tool_manager.check_status("git")
        return DependencyCheck(
            category="git",
            name="Git",
            ok=status.installed,
            detail=(
                f"Installed: {status.version}" if status.version else "Not installed"
            ),
            fix=None if status.installed else _FIX_TEMPLATES["git"],
        )

    @staticmethod
    def _package_importable(name: str) -> bool:
        """Return whether a Python package can be imported.

        ``importlib.util.find_spec`` raises ``ModuleNotFoundError`` for
        submodules of missing parent packages (e.g. ``PyQt5.QtCore`` when
        PyQt5 itself is absent), so we wrap the call defensively.

        Args:
            name: Import name to check.

        Returns:
            bool: ``True`` if the package can be imported.
        """
        try:
            return importlib.util.find_spec(name) is not None
        except (ModuleNotFoundError, ValueError):
            return False

    def _check_packages(self) -> list[DependencyCheck]:
        """Verify each required Python package is importable."""
        checks: list[DependencyCheck] = []
        for package in REQUIRED_PACKAGES:
            ok = self._package_importable(package)
            if not ok:
                # Some packages install under a different import name.
                aliases = {"PyQt5": "PyQt5.QtCore"}
                spec_name = aliases.get(package, package)
                ok = self._package_importable(spec_name)
            version = None
            if ok:
                try:
                    version = importlib.metadata.version(package)
                except importlib.metadata.PackageNotFoundError:
                    version = None
            checks.append(
                DependencyCheck(
                    category="package",
                    name=package,
                    ok=ok,
                    detail=version or ("present" if ok else "missing"),
                    fix=(
                        None
                        if ok
                        else _FIX_TEMPLATES["package"].format(package=package)
                    ),
                )
            )
        return checks

    def _check_env_vars(self) -> list[DependencyCheck]:
        """Verify required environment variables are defined."""
        checks: list[DependencyCheck] = []
        for var in REQUIRED_ENV_VARS:
            ok = var in os.environ and bool(os.environ.get(var, ""))
            checks.append(
                DependencyCheck(
                    category="env_var",
                    name=var,
                    ok=ok,
                    detail=f"Set to: {os.environ.get(var, '')[:60]}" if ok else "Not set",
                    fix=None if ok else _FIX_TEMPLATES["env_var"].format(var=var),
                )
            )
        return checks

    def _check_missing_binaries(self) -> list[DependencyCheck]:
        """Check for the core eSim binaries (KiCad, Ngspice)."""
        checks: list[DependencyCheck] = []
        for tool_name in ("kicad", "ngspice"):
            status = self.tool_manager.check_status(tool_name)
            checks.append(
                DependencyCheck(
                    category="binary",
                    name=tool_name,
                    ok=status.installed,
                    detail=(
                        f"Installed: {status.version}" if status.version else "Not installed"
                    ),
                    fix=(
                        None
                        if status.installed
                        else _FIX_TEMPLATES["binary"].format(binary=tool_name)
                    ),
                )
            )
        return checks

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------
    def scan(self) -> DependencyReport:
        """Run every dependency check and aggregate the results.

        Returns:
            DependencyReport: Complete readiness report with fixes.
        """
        logger.info("Starting dependency scan ...")

        checks: list[DependencyCheck] = [
            self._check_python_version(),
            self._check_pip(),
            self._check_git(),
        ]
        checks.extend(self._check_packages())
        checks.extend(self._check_env_vars())
        checks.extend(self._check_missing_binaries())

        missing = [check for check in checks if not check.ok]
        fixes: list[str] = []
        seen: set[str] = set()
        for check in missing:
            if check.fix and check.fix not in seen:
                fixes.append(check.fix)
                seen.add(check.fix)

        report = DependencyReport(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            system=self.system,
            checks=checks,
            missing=missing,
            fixes=fixes,
            ready=len(missing) == 0,
        )
        logger.info(
            "Scan complete: %d checks, %d failed, ready=%s",
            report.passed_count + report.failed_count,
            report.failed_count,
            report.ready,
        )
        return report