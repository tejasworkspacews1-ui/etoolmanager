# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/utils/subprocess_runner.py
# Purpose      : Safe, reusable subprocess wrapper with output capture.
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

"""Subprocess helper functions for eToolManager.

The functions in this module wrap :mod:`subprocess` so that callers can
run external commands, capture stdout/stderr, and react to failures in a
consistent, testable manner.  All commands are executed with a timeout to
prevent a hung process from blocking the application forever.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from etoolmanager.utils.logger import get_logger

logger = get_logger(__name__)

# Default timeout (seconds) for every subprocess call.
DEFAULT_TIMEOUT: int = 60


@dataclass
class CommandResult:
    """Structured result of a subprocess invocation.

    Attributes:
        returncode: Process exit code (0 indicates success on POSIX).
        stdout: Captured standard output as text.
        stderr: Captured standard error as text.
        command: The command list that was executed (for debugging).
    """

    returncode: int
    stdout: str = ""
    stderr: str = ""
    command: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Whether the command exited successfully (returncode == 0)."""
        return self.returncode == 0

    def __str__(self) -> str:
        """Human-readable summary for logging and debugging."""
        status = "OK" if self.ok else f"FAILED({self.returncode})"
        return f"[{status}] {' '.join(self.command)}"


def run_command(
    command: list[str],
    *,
    timeout: int = DEFAULT_TIMEOUT,
    cwd: Path | None = None,
    check: bool = False,
    env: dict[str, str] | None = None,
) -> CommandResult:
    """Execute a command and capture its output.

    Args:
        command: List of command tokens, e.g. ``["git", "--version"]``.
        timeout: Maximum seconds to wait before raising a timeout error.
        cwd: Optional working directory for the child process.
        check: If ``True`` raise :class:`RuntimeError` on non-zero exit.
        env: Optional environment variable overrides for the child process.

    Returns:
        CommandResult: Captured output and exit status.

    Raises:
        FileNotFoundError: If the requested executable does not exist.
        RuntimeError: If ``check`` is ``True`` and the exit code is non-zero.
    """
    logger.debug("Running: %s (cwd=%s, timeout=%ss)", " ".join(command), cwd, timeout)

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        logger.error("Command timed out after %s seconds: %s", timeout, command)
        raise RuntimeError(f"Command timed out after {timeout}s: {' '.join(command)}") from exc
    except FileNotFoundError as exc:
        logger.error("Executable not found: %s", command[0] if command else "<empty>")
        raise

    result = CommandResult(
        returncode=proc.returncode,
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
        command=list(command),
    )

    if check and not result.ok:
        logger.error("Command failed (%s): %s", result, result.stderr)
        raise RuntimeError(f"Command failed: {result}\n{result.stderr}")

    logger.debug("Command result: %s", result)
    return result


def which(executable: str) -> Path | None:
    """Locate an executable on the system PATH.

    Args:
        executable: Name of the program, e.g. ``"git"`` or ``"python"``.

    Returns:
        Path | None: Absolute path to the executable or ``None`` if missing.
    """
    found = shutil.which(executable)
    return Path(found) if found else None


def command_exists(executable: str) -> bool:
    """Return ``True`` if the given executable is present on PATH.

    Args:
        executable: Name of the program to look for.

    Returns:
        bool: Whether the executable can be found.
    """
    return which(executable) is not None