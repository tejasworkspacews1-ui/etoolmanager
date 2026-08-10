# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/tests/test_version.py
# Purpose      : Unit tests for version parsing and comparison.
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

"""Tests for :mod:`etoolmanager.utils.version`."""

from __future__ import annotations

from etoolmanager.utils.version import Version, parse_version, version_meets_minimum


class TestParseVersion:
    """Tests for the ``parse_version`` function."""

    def test_parses_simple_version(self) -> None:
        """A plain dotted version should parse correctly."""
        version = parse_version("2.43.0")
        assert version is not None
        assert version.major == 2
        assert version.minor == 43
        assert version.patch == 0

    def test_parses_version_from_tool_output(self) -> None:
        """Version embedded in tool output should be extracted."""
        version = parse_version("git version 2.43.0.windows.1")
        assert version is not None
        assert version.major == 2
        assert version.minor == 43
        assert version.patch == 0

    def test_parses_two_part_version(self) -> None:
        """A two-part version should default patch to 0."""
        version = parse_version("Python 3.11")
        assert version is not None
        assert version.major == 3
        assert version.minor == 11
        assert version.patch == 0

    def test_returns_none_for_no_version(self) -> None:
        """Text without a version should return None."""
        assert parse_version("no version here") is None

    def test_returns_none_for_empty_string(self) -> None:
        """Empty string should return None."""
        assert parse_version("") is None


class TestVersionComparison:
    """Tests for Version ordering operators."""

    def test_less_than(self) -> None:
        """Version 1.0.0 should be less than 2.0.0."""
        assert Version(1, 0, 0) < Version(2, 0, 0)

    def test_greater_than(self) -> None:
        """Version 2.1.0 should be greater than 2.0.9."""
        assert Version(2, 1, 0) > Version(2, 0, 9)

    def test_equality(self) -> None:
        """Versions with same components should be equal."""
        assert Version(3, 11, 9) == Version(3, 11, 9)

    def test_less_than_or_equal(self) -> None:
        """Version 1.0.0 should be <= 1.0.0."""
        assert Version(1, 0, 0) <= Version(1, 0, 0)

    def test_greater_than_or_equal(self) -> None:
        """Version 2.0.0 should be >= 1.9.9."""
        assert Version(2, 0, 0) >= Version(1, 9, 9)

    def test_string_representation(self) -> None:
        """String form should be major.minor.patch."""
        assert str(Version(3, 11, 9)) == "3.11.9"


class TestVersionMeetsMinimum:
    """Tests for the ``version_meets_minimum`` helper."""

    def test_meets_when_equal(self) -> None:
        """Version equal to minimum should pass."""
        assert version_meets_minimum(Version(3, 8, 0), Version(3, 8, 0))

    def test_meets_when_higher(self) -> None:
        """Version above minimum should pass."""
        assert version_meets_minimum(Version(3, 11, 9), Version(3, 8, 0))

    def test_fails_when_lower(self) -> None:
        """Version below minimum should fail."""
        assert not version_meets_minimum(Version(3, 7, 0), Version(3, 8, 0))

    def test_fails_when_none(self) -> None:
        """None version should always fail."""
        assert not version_meets_minimum(None, Version(3, 8, 0))