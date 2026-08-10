# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/test_os_detector.py
# Purpose      : Unit tests for OS detection logic.
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

"""Tests for :mod:`etoolmanager.core.os_detector`."""

from __future__ import annotations

from pathlib import Path

import pytest

from etoolmanager.core import os_detector
from etoolmanager.core.os_detector import (
    OS_ARCH,
    OS_DEBIAN,
    OS_FEDORA,
    OS_MACOS,
    OS_UBUNTU,
    OS_UNKNOWN,
    OS_WINDOWS,
    SystemInfo,
    _detect_package_manager,
    _read_os_release,
    detect_system,
    is_linux,
    is_macos,
    is_windows,
)


class TestReadOsRelease:
    """Tests for parsing /etc/os-release."""

    def test_reads_ubuntu_release(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A valid os-release file should parse key/value pairs."""
        fake = tmp_path / "os-release"
        fake.write_text(
            'ID=ubuntu\nPRETTY_NAME="Ubuntu 22.04.3 LTS"\nVERSION_ID="22.04"\n',
            encoding="utf-8",
        )
        # Patch the module-level Path reference so only the os-release
        # lookup is affected, not the fake file's own read_text call.
        class FakePath:
            """Minimal stand-in for pathlib.Path used by _read_os_release."""

            def __init__(self, *args, **kwargs) -> None:
                """Accept and ignore the path argument."""
                pass

            @staticmethod
            def exists() -> bool:
                """Pretend the file always exists."""
                return True

            @staticmethod
            def read_text(*args, **kwargs) -> str:
                """Return the fake os-release content."""
                return fake.read_text(encoding="utf-8")

        monkeypatch.setattr(os_detector, "Path", FakePath)

        fields = _read_os_release()
        assert fields["ID"] == "ubuntu"
        assert fields["PRETTY_NAME"] == "Ubuntu 22.04.3 LTS"

    def test_returns_empty_when_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A missing os-release file should return an empty dict."""
        monkeypatch.setattr(os_detector.Path, "exists", lambda *_: False)
        assert _read_os_release() == {}


class TestDetectPackageManager:
    """Tests for the package-manager mapping."""

    @pytest.mark.parametrize(
        ("os_name", "expected"),
        [
            (OS_UBUNTU, "apt-get"),
            (OS_DEBIAN, "apt-get"),
            (OS_FEDORA, "dnf"),
            (OS_ARCH, "pacman"),
            (OS_WINDOWS, "winget"),
            (OS_MACOS, "brew"),
            (OS_UNKNOWN, "unknown"),
        ],
    )
    def test_mapping(self, os_name: str, expected: str) -> None:
        """Each OS key should map to the right package manager."""
        assert _detect_package_manager(os_name) == expected


class TestSystemInfo:
    """Tests for the SystemInfo dataclass."""

    def test_to_dict(self, sample_system: SystemInfo) -> None:
        """to_dict should return a plain dictionary with all fields."""
        data = sample_system.to_dict()
        assert data["os_name"] == "ubuntu"
        assert data["os_display"] == "Ubuntu 22.04"
        assert data["package_manager"] == "apt-get"
        assert data["python_version"] == "3.11.9"


class TestDetectSystem:
    """Tests for the full system detection."""

    def test_returns_system_info(self) -> None:
        """detect_system should always return a SystemInfo."""
        info = detect_system()
        assert isinstance(info, SystemInfo)
        assert info.os_name in {
            OS_UBUNTU,
            OS_DEBIAN,
            OS_FEDORA,
            OS_ARCH,
            OS_WINDOWS,
            OS_MACOS,
            OS_UNKNOWN,
        }
        assert info.architecture
        assert info.python_version


class TestPlatformHelpers:
    """Tests for is_windows/is_macos/is_linux helpers."""

    def test_at_least_one_returns_true(self) -> None:
        """Exactly one of the platform helpers should be true."""
        results = [is_windows(), is_macos(), is_linux()]
        assert sum(results) == 1