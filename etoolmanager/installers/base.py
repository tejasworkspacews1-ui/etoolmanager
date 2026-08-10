# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/installers/base.py
# Purpose      : Abstract installer interface (Strategy pattern).
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

"""Abstract base class for platform-specific tool installers.

The installer classes follow the Strategy pattern: the :class:`ToolManager`
decides which strategy to use based on the detected OS, and each concrete
installer only knows how to execute commands for its own platform.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from etoolmanager.config.loader import ToolConfig
from etoolmanager.utils.subprocess_runner import CommandResult


class BaseInstaller(ABC):
    """Interface implemented by every platform installer.

    Attributes:
        tool: Configuration of the tool to install/uninstall.
    """

    def __init__(self, tool: ToolConfig) -> None:
        """Initialise the installer with a tool configuration.

        Args:
            tool: Tool registry entry.
        """
        self.tool = tool

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the canonical OS key this installer supports.

        Returns:
            str: One of ``ubuntu``, ``debian``, ``fedora``, ``arch``,
                ``windows``, or ``macos``.
        """
        raise NotImplementedError

    @abstractmethod
    def install(self) -> CommandResult:
        """Install the tool on this platform.

        Returns:
            CommandResult: Standardised subprocess result.
        """
        raise NotImplementedError

    @abstractmethod
    def uninstall(self) -> CommandResult:
        """Uninstall the tool from this platform.

        Returns:
            CommandResult: Standardised subprocess result.
        """
        raise NotImplementedError