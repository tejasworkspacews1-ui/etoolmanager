# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/installers/factory.py
# Purpose      : Factory that builds the right installer for the current OS.
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

"""Installer factory following the Factory Method pattern.

The factory inspects the detected OS key and returns the concrete
installer strategy.  New platforms can be added by extending the mapping
without touching the caller.
"""

from __future__ import annotations

from etoolmanager.config.loader import ToolConfig
from etoolmanager.installers.base import BaseInstaller
from etoolmanager.installers.package_manager import PackageManagerInstaller


class InstallerFactory:
    """Create the appropriate installer for a platform/tool pair."""

    @staticmethod
    def create(tool: ToolConfig, platform_name: str) -> BaseInstaller:
        """Return an installer instance for the given platform.

        Args:
            tool: Tool registry entry to install/uninstall.
            platform_name: Canonical OS key (``ubuntu``, ``windows``, ...).

        Returns:
            BaseInstaller: Concrete installer that can install the tool.

        Raises:
            ValueError: If the platform is not recognised.
        """
        supported = {
            "ubuntu",
            "debian",
            "fedora",
            "arch",
            "windows",
            "macos",
        }
        if platform_name not in supported:
            raise ValueError(f"Unsupported platform: {platform_name}")

        # All current tools use the package-manager strategy.  If a future
        # tool needs a custom installer (e.g. downloading an AppImage),
        # extend this factory with a registry of strategies.
        return PackageManagerInstaller(tool=tool, platform_name=platform_name)