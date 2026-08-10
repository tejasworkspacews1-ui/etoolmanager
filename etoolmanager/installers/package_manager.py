# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/installers/package_manager.py
# Purpose      : Concrete installer that delegates to the OS package manager.
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

"""Installer that runs the platform package-manager command.

This is the default strategy for all four supported tools.  It reads the
install/uninstall command lists from the YAML registry and executes them
with the subprocess runner, prepending ``sudo`` on POSIX systems.
"""

from __future__ import annotations

from etoolmanager.config.loader import ToolConfig
from etoolmanager.installers.base import BaseInstaller
from etoolmanager.utils.logger import get_logger
from etoolmanager.utils.subprocess_runner import CommandResult, run_command

logger = get_logger(__name__)

# OS keys that require elevated privileges for package operations.
_POSIX_OS_KEYS = {"ubuntu", "debian", "fedora", "arch", "macos"}


class PackageManagerInstaller(BaseInstaller):
    """Install/uninstall a tool via the system package manager.

    Attributes:
        platform_name: Canonical OS key this installer targets.
    """

    def __init__(self, tool: ToolConfig, platform_name: str) -> None:
        """Initialise the installer.

        Args:
            tool: Tool registry entry.
            platform_name: Canonical OS key (``ubuntu``, ``windows``, ...).
        """
        super().__init__(tool)
        self._platform_name = platform_name

    @property
    def platform_name(self) -> str:
        """Return the canonical OS key this installer supports."""
        return self._platform_name

    def _resolve_command(self, action: str) -> list[str]:
        """Return the command list for the requested action.

        Args:
            action: Either ``"install"`` or ``"uninstall"``.

        Returns:
            list[str]: Command tokens for the current platform.

        Raises:
            RuntimeError: If no command is defined for this platform.
        """
        commands = getattr(self.tool, action, {})
        command = commands.get(self._platform_name)
        if command is None:
            raise RuntimeError(
                f"No {action} command defined for '{self.tool.name}' "
                f"on {self._platform_name}"
            )

        # Prepend sudo on POSIX systems so the command works without
        # requiring the user to run the whole CLI as root.
        if self._platform_name in _POSIX_OS_KEYS:
            command = ["sudo", *command]
        return command

    def install(self) -> CommandResult:
        """Install the tool using the package manager.

        Returns:
            CommandResult: Standardised subprocess result.
        """
        command = self._resolve_command("install")
        logger.info("Installing %s: %s", self.tool.name, " ".join(command))
        return run_command(command, timeout=300)

    def uninstall(self) -> CommandResult:
        """Uninstall the tool using the package manager.

        Returns:
            CommandResult: Standardised subprocess result.
        """
        command = self._resolve_command("uninstall")
        logger.info("Uninstalling %s: %s", self.tool.name, " ".join(command))
        return run_command(command, timeout=300)