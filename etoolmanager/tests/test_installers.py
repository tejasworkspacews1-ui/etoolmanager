# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/test_installers.py
# Purpose      : Unit tests for the installer strategies and factory.
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

"""Tests for :mod:`etoolmanager.installers`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from etoolmanager.config.loader import get_tool
from etoolmanager.installers.base import BaseInstaller
from etoolmanager.installers.factory import InstallerFactory
from etoolmanager.installers.package_manager import PackageManagerInstaller
from etoolmanager.utils.subprocess_runner import CommandResult


class TestPackageManagerInstaller:
    """Tests for the PackageManagerInstaller."""

    def setup_method(self) -> None:
        """Load a git tool config for each test."""
        self.tool = get_tool("git")
        assert self.tool is not None

    def test_platform_name(self) -> None:
        """platform_name should return the configured OS key."""
        installer = PackageManagerInstaller(self.tool, "ubuntu")
        assert installer.platform_name == "ubuntu"

    def test_is_base_installer(self) -> None:
        """The installer should implement BaseInstaller."""
        installer = PackageManagerInstaller(self.tool, "ubuntu")
        assert isinstance(installer, BaseInstaller)

    @patch(
        "etoolmanager.installers.package_manager.run_command",
        return_value=CommandResult(returncode=0, stdout="", stderr=""),
    )
    def test_install_ubuntu_prepends_sudo(self, mock_run: MagicMock) -> None:
        """Install on Ubuntu should prepend sudo."""
        installer = PackageManagerInstaller(self.tool, "ubuntu")
        result = installer.install()

        assert result.ok
        command = mock_run.call_args.args[0]
        assert command[0] == "sudo"
        assert "apt-get" in command

    @patch(
        "etoolmanager.installers.package_manager.run_command",
        return_value=CommandResult(returncode=0, stdout="", stderr=""),
    )
    def test_install_windows_no_sudo(self, mock_run: MagicMock) -> None:
        """Install on Windows should not prepend sudo."""
        installer = PackageManagerInstaller(self.tool, "windows")
        result = installer.install()

        assert result.ok
        command = mock_run.call_args.args[0]
        assert command[0] == "winget"

    @patch(
        "etoolmanager.installers.package_manager.run_command",
        return_value=CommandResult(returncode=0, stdout="", stderr=""),
    )
    def test_uninstall_ubuntu_prepends_sudo(self, mock_run: MagicMock) -> None:
        """Uninstall on Ubuntu should prepend sudo."""
        installer = PackageManagerInstaller(self.tool, "ubuntu")
        result = installer.uninstall()

        assert result.ok
        command = mock_run.call_args.args[0]
        assert command[0] == "sudo"
        assert "remove" in command

    def test_install_unsupported_platform(self) -> None:
        """An unsupported platform should raise RuntimeError."""
        installer = PackageManagerInstaller(self.tool, "unknown")
        with pytest.raises(RuntimeError):
            installer.install()

    def test_uninstall_unsupported_platform(self) -> None:
        """An unsupported platform should raise RuntimeError."""
        installer = PackageManagerInstaller(self.tool, "unknown")
        with pytest.raises(RuntimeError):
            installer.uninstall()


class TestInstallerFactory:
    """Tests for the installer factory."""

    def test_create_returns_installer(self) -> None:
        """Factory should return a BaseInstaller for supported platforms."""
        tool = get_tool("git")
        assert tool is not None
        installer = InstallerFactory.create(tool, "ubuntu")
        assert isinstance(installer, BaseInstaller)
        assert installer.platform_name == "ubuntu"

    def test_create_unsupported_platform(self) -> None:
        """Unsupported platforms should raise ValueError."""
        tool = get_tool("git")
        assert tool is not None
        with pytest.raises(ValueError):
            InstallerFactory.create(tool, "solaris")


class TestBaseInstaller:
    """Tests for the abstract base installer."""

    def test_abstract_class_cannot_instantiate(self) -> None:
        """BaseInstaller should not be instantiable directly."""
        tool = get_tool("git")
        assert tool is not None
        with pytest.raises(TypeError):
            BaseInstaller(tool)  # type: ignore[abstract]