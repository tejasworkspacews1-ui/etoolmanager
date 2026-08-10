# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/config/loader.py
# Purpose      : Load and validate the declarative tool registry.
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

"""Load tool definitions from the bundled ``tools.yaml`` registry.

The registry is a declarative description of every tool eToolManager can
manage.  Keeping the registry in YAML (rather than Python code) means new
tools can be added by editing a data file, and platform-specific install
commands stay close to the tool they belong to.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from etoolmanager.utils.logger import get_logger

logger = get_logger(__name__)

# Default path to the bundled YAML registry.
DEFAULT_TOOLS_CONFIG: Path = Path(__file__).resolve().parent / "tools.yaml"


@dataclass(frozen=True)
class ToolConfig:
    """Immutable configuration for a single managed tool.

    Attributes:
        name: Canonical tool key, e.g. ``"git"``.
        display_name: Human-friendly name shown in the UI.
        description: Short explanation of why eSim needs the tool.
        default_version: Minimum recommended version as a string.
        version_command: Command tokens that print the version.
        version_regex: Regex used to extract the version from output.
        binary_names: Executable names used to detect the tool.
        install: Mapping of OS key -> install command tokens.
        uninstall: Mapping of OS key -> uninstall command tokens.
        required_for_esim: Whether eSim cannot run without this tool.
    """

    name: str
    display_name: str
    description: str
    default_version: str
    version_command: list[str]
    version_regex: str
    binary_names: list[str]
    install: dict[str, list[str]] = field(default_factory=dict)
    uninstall: dict[str, list[str]] = field(default_factory=dict)
    required_for_esim: bool = False


def _parse_tool(name: str, data: dict[str, Any]) -> ToolConfig:
    """Parse a single tool dictionary into a :class:`ToolConfig`.

    Args:
        name: Tool key from the YAML file.
        data: Raw mapping of tool attributes.

    Returns:
        ToolConfig: Validated configuration object.

    Raises:
        ValueError: If required keys are missing or malformed.
    """
    required = ("display_name", "description", "default_version", "version_command")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Tool '{name}' missing required keys: {', '.join(missing)}")

    return ToolConfig(
        name=name,
        display_name=str(data["display_name"]),
        description=str(data["description"]),
        default_version=str(data["default_version"]),
        version_command=[str(item) for item in data["version_command"]],
        version_regex=str(data.get("version_regex", r"(\\d+\\.\\d+(?:\\.\\d+)?)")),
        binary_names=[str(item) for item in data.get("binary_names", [name])],
        install={
            str(os_key): [str(cmd) for cmd in cmds]
            for os_key, cmds in data.get("install", {}).items()
        },
        uninstall={
            str(os_key): [str(cmd) for cmd in cmds]
            for os_key, cmds in data.get("uninstall", {}).items()
        },
        required_for_esim=bool(data.get("required_for_esim", False)),
    )


@lru_cache(maxsize=1)
def load_tool_config(path: Path | None = None) -> dict[str, ToolConfig]:
    """Load the complete tool registry from YAML.

    Args:
        path: Optional override for the YAML registry path.

    Returns:
        dict[str, ToolConfig]: Mapping of tool name to configuration.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        yaml.YAMLError: If the YAML is malformed.
    """
    registry_path = path or DEFAULT_TOOLS_CONFIG
    logger.debug("Loading tool registry from %s", registry_path)

    with registry_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    tools_raw = raw.get("tools", {})
    if not isinstance(tools_raw, dict):
        raise ValueError("Expected 'tools' to be a mapping in the registry")

    registry: dict[str, ToolConfig] = {}
    for name, data in tools_raw.items():
        if isinstance(data, dict):
            registry[name] = _parse_tool(name, data)

    logger.info("Loaded %d tool definitions", len(registry))
    return registry


def get_tool(name: str) -> ToolConfig | None:
    """Return the configuration for a single tool.

    Args:
        name: Tool key, e.g. ``"git"``.

    Returns:
        ToolConfig | None: The tool config or ``None`` if unknown.
    """
    return load_tool_config().get(name)