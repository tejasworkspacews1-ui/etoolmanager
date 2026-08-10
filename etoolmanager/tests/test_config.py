# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/test_config.py
# Purpose      : Unit tests for the YAML tool registry loader.
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

"""Tests for :mod:`etoolmanager.config.loader`."""

from __future__ import annotations

import pytest

from etoolmanager.config import loader
from etoolmanager.config.loader import get_tool, load_tool_config


class TestLoadToolConfig:
    """Tests for loading the YAML registry."""

    def test_loads_all_tools(self) -> None:
        """The bundled registry should contain all four tools."""
        registry = load_tool_config()
        assert {"git", "python", "kicad", "ngspice"}.issubset(registry.keys())

    def test_tool_config_fields(self) -> None:
        """Each tool config should have valid fields."""
        git = get_tool("git")
        assert git is not None
        assert git.name == "git"
        assert git.display_name == "Git"
        assert git.version_command == ["git", "--version"]
        assert "ubuntu" in git.install
        assert "windows" in git.install

    def test_unknown_tool_returns_none(self) -> None:
        """Unknown tool names should return None."""
        assert get_tool("nonexistent") is None


class TestParseTool:
    """Tests for the ToolConfig parsing validation."""

    def test_parse_missing_required_keys(self) -> None:
        """Missing required keys should raise ValueError."""
        with pytest.raises(ValueError):
            loader._parse_tool("tool1", {"display_name": "Tool"})

    def test_parse_valid_tool(self) -> None:
        """A complete tool dict should parse to a ToolConfig."""
        config = loader._parse_tool(
            "git",
            {
                "display_name": "Git",
                "description": "Version control",
                "default_version": "2.25.0",
                "version_command": ["git", "--version"],
                "version_regex": "git version (\\d+\\.\\d+)",
                "binary_names": ["git"],
                "install": {"ubuntu": ["apt-get", "install", "git"]},
                "uninstall": {"ubuntu": ["apt-get", "remove", "git"]},
                "required_for_esim": True,
            },
        )
        assert config.name == "git"
        assert config.display_name == "Git"
        assert config.required_for_esim is True
        assert config.install["ubuntu"] == ["apt-get", "install", "git"]