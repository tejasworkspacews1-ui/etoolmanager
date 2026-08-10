# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/utils/version.py
# Purpose      : Parse and compare version strings from tool outputs.
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

"""Version parsing and comparison helpers.

Tools such as ``git --version`` or ``python --version`` emit version
strings in slightly different formats.  This module provides a small,
dependency-free parser that extracts a comparable ``(major, minor, patch)``
tuple from arbitrary text, plus helpers to compare versions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Matches a dotted numeric version, e.g. "2.43.0" or "3.11.9".
_VERSION_RE = re.compile(r"(\d+)\.(\d+)(?:\.(\d+))?")


@dataclass(frozen=True)
class Version:
    """A parsed semantic version.

    Attributes:
        major: Major version number.
        minor: Minor version number.
        patch: Patch version number (0 if not present in the string).
        raw: The original string the version was parsed from.
    """

    major: int
    minor: int
    patch: int = 0
    raw: str = ""

    def __str__(self) -> str:
        """Return the canonical ``major.minor.patch`` representation."""
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: object) -> bool:
        """Compare two versions numerically (major, then minor, then patch)."""
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __le__(self, other: object) -> bool:
        """Compare two versions numerically (<=)."""
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) <= (
            other.major,
            other.minor,
            other.patch,
        )

    def __gt__(self, other: object) -> bool:
        """Compare two versions numerically (>)."""
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) > (
            other.major,
            other.minor,
            other.patch,
        )

    def __ge__(self, other: object) -> bool:
        """Compare two versions numerically (>=)."""
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) >= (
            other.major,
            other.minor,
            other.patch,
        )

    def __eq__(self, other: object) -> bool:
        """Compare two versions for equality."""
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )


def parse_version(text: str) -> Version | None:
    """Extract the first dotted numeric version from arbitrary text.

    Args:
        text: Raw output from a tool, e.g. ``"git version 2.43.0"``.

    Returns:
        Version | None: Parsed version, or ``None`` if no version found.
    """
    match = _VERSION_RE.search(text)
    if not match:
        return None

    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3)) if match.group(3) else 0
    return Version(major=major, minor=minor, patch=patch, raw=text.strip())


def version_meets_minimum(version: Version | None, minimum: Version) -> bool:
    """Return ``True`` if ``version`` is at least ``minimum``.

    Args:
        version: Parsed version of the installed tool (may be ``None``).
        minimum: Minimum acceptable version.

    Returns:
        bool: ``False`` when ``version`` is ``None`` or below the minimum.
    """
    if version is None:
        return False
    return version >= minimum