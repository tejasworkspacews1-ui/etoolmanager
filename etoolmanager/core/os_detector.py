# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/core/os_detector.py
# Purpose      : Cross-platform operating system and package manager detection.
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

"""Detect the host operating system, distribution, and package manager.

The detector inspects :mod:`platform` and, on Linux, the ``/etc/os-release``
file to identify the distribution.  It also maps each OS to the package
manager that eToolManager will use for install/uninstall commands.
"""

from __future__ import annotations

import platform
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from etoolmanager.utils.logger import get_logger

logger = get_logger(__name__)

# Canonical OS keys used throughout the tool registry.
OS_UBUNTU = "ubuntu"
OS_DEBIAN = "debian"
OS_FEDORA = "fedora"
OS_ARCH = "arch"
OS_WINDOWS = "windows"
OS_MACOS = "macos"
OS_UNKNOWN = "unknown"

# Mapping of package manager -> canonical OS key.
_PACKAGE_MANAGER_OS = {
    "apt-get": OS_UBUNTU,
    "apt": OS_UBUNTU,
    "dnf": OS_FEDORA,
    "yum": OS_FEDORA,
    "pacman": OS_ARCH,
    "winget": OS_WINDOWS,
    "choco": OS_WINDOWS,
    "brew": OS_MACOS,
}


@dataclass(frozen=True)
class SystemInfo:
    """Immutable snapshot of the detected system.

    Attributes:
        os_name: Canonical OS key (``ubuntu``, ``windows``, ...).
        os_display: Human-friendly OS name, e.g. ``"Ubuntu 22.04"``.
        version: OS version string.
        architecture: Machine architecture, e.g. ``"x86_64"``.
        package_manager: Detected package manager executable.
        python_version: Running Python version.
    """

    os_name: str
    os_display: str
    version: str
    architecture: str
    package_manager: str
    python_version: str

    def to_dict(self) -> dict[str, str]:
        """Return the system info as a plain dictionary for reports."""
        return {
            "os_name": self.os_name,
            "os_display": self.os_display,
            "version": self.version,
            "architecture": self.architecture,
            "package_manager": self.package_manager,
            "python_version": self.python_version,
        }


def _read_os_release() -> dict[str, str]:
    """Parse ``/etc/os-release`` into a dictionary.

    Returns:
        dict[str, str]: Key/value pairs from the file (empty if missing).
    """
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return {}

    fields: dict[str, str] = {}
    try:
        for line in os_release.read_text(encoding="utf-8").splitlines():
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            fields[key.strip()] = value.strip().strip('"')
    except OSError as exc:
        logger.warning("Could not read /etc/os-release: %s", exc)

    return fields


def _detect_linux_distro() -> tuple[str, str]:
    """Identify the Linux distribution name and version.

    Returns:
        tuple[str, str]: ``(canonical_os_key, display_name)``.
    """
    fields = _read_os_release()
    distro_id = fields.get("ID", "").lower()
    pretty_name = fields.get("PRETTY_NAME", fields.get("NAME", "Linux"))

    if distro_id in ("ubuntu", "debian"):
        return distro_id, pretty_name
    if distro_id in ("fedora", "rhel", "centos"):
        return OS_FEDORA, pretty_name
    if distro_id in ("arch", "manjaro", "endeavouros"):
        return OS_ARCH, pretty_name

    # Fallback: try platform.linux_distribution (deprecated but useful).
    try:
        distro = platform.linux_distribution()  # type: ignore[attr-defined]
        if distro and distro[0]:
            name = distro[0].lower()
            if "ubuntu" in name or "debian" in name:
                return OS_UBUNTU, pretty_name
            if "fedora" in name or "centos" in name or "rhel" in name:
                return OS_FEDORA, pretty_name
            if "arch" in name:
                return OS_ARCH, pretty_name
    except (AttributeError, OSError):
        pass

    return OS_UNKNOWN, pretty_name


def _detect_package_manager(os_name: str) -> str:
    """Return the package manager for the detected OS.

    Args:
        os_name: Canonical OS key.

    Returns:
        str: Package manager name, or ``"unknown"`` if not recognised.
    """
    if os_name == OS_UBUNTU or os_name == OS_DEBIAN:
        return "apt-get"
    if os_name == OS_FEDORA:
        return "dnf"
    if os_name == OS_ARCH:
        return "pacman"
    if os_name == OS_WINDOWS:
        return "winget"
    if os_name == OS_MACOS:
        return "brew"
    return "unknown"


def detect_system() -> SystemInfo:
    """Detect the current operating system and return a snapshot.

    Returns:
        SystemInfo: Detected OS, version, architecture, and package manager.
    """
    system = platform.system().lower()
    architecture = platform.machine() or platform.processor() or "unknown"
    python_version = platform.python_version()

    if system == "windows":
        os_name = OS_WINDOWS
        os_display = f"Windows {platform.release()}"
        version = platform.version()
    elif system == "darwin":
        os_name = OS_MACOS
        os_display = f"macOS {platform.mac_ver()[0]}"
        version = platform.mac_ver()[0]
    elif system == "linux":
        os_name, os_display = _detect_linux_distro()
        version = platform.release()
    else:
        os_name = OS_UNKNOWN
        os_display = platform.system() or "Unknown"
        version = platform.release()

    package_manager = _detect_package_manager(os_name)

    info = SystemInfo(
        os_name=os_name,
        os_display=os_display,
        version=version,
        architecture=architecture,
        package_manager=package_manager,
        python_version=python_version,
    )
    logger.info(
        "Detected system: %s (%s), arch=%s, pkg=%s",
        info.os_display,
        info.os_name,
        info.architecture,
        info.package_manager,
    )
    return info


def is_windows() -> bool:
    """Return ``True`` when running on Windows."""
    return sys.platform.startswith("win")


def is_macos() -> bool:
    """Return ``True`` when running on macOS."""
    return sys.platform == "darwin"


def is_linux() -> bool:
    """Return ``True`` when running on Linux."""
    return sys.platform.startswith("linux")