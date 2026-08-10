# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/core/tool_manager.py
# Purpose      : High-level tool lifecycle management (detect, install,
#                uninstall, version check).
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

"""Tool lifecycle management.

The :class:`ToolManager` is the facade that the CLI and other components
use to interact with the four supported tools.  It resolves the right
platform command from the YAML registry, talks to the subprocess runner,
and returns a structured :class:`ToolStatus` that the UI layers render.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from etoolmanager.config.loader import ToolConfig, get_tool, load_tool_config
from etoolmanager.core.os_detector import SystemInfo, detect_system
from etoolmanager.utils.logger import get_logger
from etoolmanager.utils.subprocess_runner import (
    CommandResult,
    command_exists,
    run_command,
)
from etoolmanager.utils.version import Version, parse_version, version_meets_minimum

logger = get_logger(__name__)


@dataclass
class ToolStatus:
    """Status snapshot for one managed tool.

    Attributes:
        name: Canonical tool key.
        installed: Whether a binary was found on the system.
        version: Parsed installed version (``None`` if not installed).
        minimum_version: Recommended minimum version from the registry.
        meets_minimum: Whether the installed version passes the check.
        command_used: The binary that was found, if any.
        error: Optional error message from detection or version calls.
    """

    name: str
    installed: bool = False
    version: Version | None = None
    minimum_version: Version | None = None
    meets_minimum: bool = False
    command_used: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the status as a plain dictionary for reports."""
        return {
            "name": self.name,
            "installed": self.installed,
            "version": str(self.version) if self.version else None,
            "minimum_version": (
                str(self.minimum_version) if self.minimum_version else None
            ),
            "meets_minimum": self.meets_minimum,
            "command_used": self.command_used,
            "error": self.error,
        }


class ToolManager:
    """Facade coordinating tool lifecycle operations.

    Attributes:
        system: Detected :class:`SystemInfo` for the current host.
    """

    def __init__(self, system: SystemInfo | None = None) -> None:
        """Initialise the manager with an optional pre-detected system.

        Args:
            system: Pre-detected system info (defaults to auto-detect).
        """
        self.system = system or detect_system()

    # ------------------------------------------------------------------
    # Detection helpers
    # ------------------------------------------------------------------
    def _find_binary(self, config: ToolConfig) -> str | None:
        """Return the first available binary name from the registry.

        Args:
            config: Tool configuration.

        Returns:
            str | None: Executable name found on PATH, or ``None``.
        """
        for binary in config.binary_names:
            if command_exists(binary):
                return binary
        return None

    def _executable_version(self, binary: str, config: ToolConfig) -> Version | None:
        """Detect the installed version using the registry version command.

        Args:
            binary: Executable name that was found.
            config: Tool configuration.

        Returns:
            Version | None: Parsed version or ``None`` on failure.
        """
        try:
            result = run_command(config.version_command)
        except (RuntimeError, FileNotFoundError) as exc:
            logger.warning("Version check failed for %s: %s", config.name, exc)
            return None

        if not result.ok:
            logger.warning(
                "Version command returned %d for %s", result.returncode, config.name
            )
            return None

        pattern = re.compile(config.version_regex)
        match = pattern.search(result.stdout)
        if match:
            return parse_version(match.group(0))
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def check_status(self, tool_name: str) -> ToolStatus:
        """Check whether a tool is installed and its version.

        Args:
            tool_name: Canonical tool key (``git``, ``python``, ...).

        Returns:
            ToolStatus: Detection result with version and minimum comparison.

        Raises:
            ValueError: If the tool is not in the registry.
        """
        config = get_tool(tool_name)
        if config is None:
            raise ValueError(f"Unknown tool: {tool_name}")

        minimum = parse_version(config.default_version)
        binary = self._find_binary(config)

        if binary is None:
            logger.info("Tool '%s' is NOT installed", tool_name)
            return ToolStatus(
                name=tool_name,
                installed=False,
                minimum_version=minimum,
                meets_minimum=False,
            )

        version = self._executable_version(binary, config)
        meets = version_meets_minimum(version, minimum) if minimum else bool(version)

        logger.info(
            "Tool '%s' installed=%s binary=%s version=%s meets_min=%s",
            tool_name,
            True,
            binary,
            version,
            meets,
        )
        return ToolStatus(
            name=tool_name,
            installed=True,
            version=version,
            minimum_version=minimum,
            meets_minimum=meets,
            command_used=binary,
        )

    def check_all(self) -> list[ToolStatus]:
        """Check the status of every tool in the registry.

        Returns:
            list[ToolStatus]: Status for each registered tool.
        """
        configs = load_tool_config()
        statuses: list[ToolStatus] = []
        for name in configs:
            try:
                statuses.append(self.check_status(name))
            except (ValueError, RuntimeError) as exc:
                logger.error("Failed to check '%s': %s", name, exc)
                statuses.append(
                    ToolStatus(name=name, installed=False, error=str(exc))
                )
        return statuses

    def install(self, tool_name: str) -> CommandResult:
        """Install a tool using the platform-specific package manager.

        Args:
            tool_name: Canonical tool key.

        Returns:
            CommandResult: Output of the install command.

        Raises:
            ValueError: If the tool is unknown.
            RuntimeError: If the platform has no install command defined.
        """
        config = get_tool(tool_name)
        if config is None:
            raise ValueError(f"Unknown tool: {tool_name}")

        command = config.install.get(self.system.os_name)
        if command is None:
            raise RuntimeError(
                f"No install command defined for '{tool_name}' on {self.system.os_name}"
            )

        # On Linux/macOS installs may need elevated privileges.  We prepend
        # sudo when the current user is not root to make the command work
        # out of the box on developer machines.
        if self.system.os_name in ("ubuntu", "debian", "fedora", "arch", "macos"):
            command = ["sudo", *command]

        logger.info("Installing %s: %s", tool_name, " ".join(command))
        return run_command(command, timeout=300)

    def uninstall(self, tool_name: str) -> CommandResult:
        """Uninstall a tool using the platform-specific command.

        Args:
            tool_name: Canonical tool key.

        Returns:
            CommandResult: Output of the uninstall command.

        Raises:
            ValueError: If the tool is unknown.
            RuntimeError: If the platform has no uninstall command defined.
        """
        config = get_tool(tool_name)
        if config is None:
            raise ValueError(f"Unknown tool: {tool_name}")

        command = config.uninstall.get(self.system.os_name)
        if command is None:
            raise RuntimeError(
                f"No uninstall command defined for '{tool_name}' on {self.system.os_name}"
            )

        if self.system.os_name in ("ubuntu", "debian", "fedora", "arch", "macos"):
            command = ["sudo", *command]

        logger.info("Uninstalling %s: %s", tool_name, " ".join(command))
        return run_command(command, timeout=300)