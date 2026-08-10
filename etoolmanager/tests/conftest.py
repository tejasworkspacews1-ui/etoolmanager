# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/conftest.py
# Purpose      : Shared pytest fixtures for the eToolManager test suite.
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

"""Shared fixtures used across the eToolManager test modules."""

from __future__ import annotations

from pathlib import Path

import pytest

from etoolmanager.core.os_detector import SystemInfo


@pytest.fixture
def sample_system() -> SystemInfo:
    """Return a deterministic SystemInfo for tests."""
    return SystemInfo(
        os_name="ubuntu",
        os_display="Ubuntu 22.04",
        version="22.04",
        architecture="x86_64",
        package_manager="apt-get",
        python_version="3.11.9",
    )


@pytest.fixture
def windows_system() -> SystemInfo:
    """Return a Windows SystemInfo for platform-specific tests."""
    return SystemInfo(
        os_name="windows",
        os_display="Windows 11",
        version="10.0.22631",
        architecture="AMD64",
        package_manager="winget",
        python_version="3.11.9",
    )


@pytest.fixture
def tmp_report_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for report output tests."""
    return tmp_path / "reports"