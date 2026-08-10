# =============================================================================
# Project      : eToolManager
# File         : etoolmanager/cli/app.py
# Purpose      : Typer-based command-line interface for eToolManager.
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

"""Command-line interface for eToolManager.

The CLI is intentionally a thin presentation layer: it parses commands,
delegates to the business logic in :mod:`etoolmanager.core` and
:mod:`etoolmanager.dependency`, and renders results with Rich.  All
business rules live outside this module so the same logic can be reused
by a GUI or an API server in the future.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from etoolmanager.core.os_detector import detect_system
from etoolmanager.core.tool_manager import ToolManager
from etoolmanager.dependency.scanner import DependencyScanner
from etoolmanager.reports.generator import (
    generate_json_report,
    generate_markdown_report,
)
from etoolmanager.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

app = typer.Typer(
    name="etoolmanager",
    help="Automated tool manager for the eSim ecosystem.",
    add_completion=False,
)
console = Console()

# Supported tools advertised in help text.
SUPPORTED_TOOLS = "git, python, kicad, ngspice"


@app.callback()
def main(
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable DEBUG logging.")
    ] = False,
) -> None:
    """Global CLI entry point with logging configuration."""
    level = "DEBUG" if verbose else "INFO"
    setup_logging(level=level)


@app.command("system")
def system_info() -> None:
    """Display detailed information about the detected operating system."""
    info = detect_system()
    console.print(
        Panel(
            "[bold cyan]eToolManager - System Information[/bold cyan]\n\n"
            f"[bold]OS:[/bold] {info.os_display} ({info.os_name})\n"
            f"[bold]Version:[/bold] {info.version}\n"
            f"[bold]Architecture:[/bold] {info.architecture}\n"
            f"[bold]Package Manager:[/bold] {info.package_manager}\n"
            f"[bold]Python:[/bold] {info.python_version}",
            title="System",
            border_style="cyan",
        )
    )


@app.command("status")
def tool_status(
    tool: Annotated[
        Optional[str],
        typer.Argument(help="Tool name (git, python, kicad, ngspice). Omit for all."),
    ] = None,
) -> None:
    """Check whether a tool is installed and its version."""
    manager = ToolManager()

    if tool:
        try:
            status = manager.check_status(tool)
            _render_status_table([status])
        except ValueError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1)
    else:
        statuses = manager.check_all()
        _render_status_table(statuses)


def _render_status_table(statuses: list) -> None:
    """Render a list of ToolStatus objects as a Rich table.

    Args:
        statuses: Tool status snapshots to display.
    """
    table = Table(title="eToolManager - Tool Status", box=box.ROUNDED)
    table.add_column("Tool", style="bold cyan")
    table.add_column("Installed", justify="center")
    table.add_column("Version")
    table.add_column("Minimum", style="dim")
    table.add_column("Meets Min", justify="center")

    for status in statuses:
        installed = "[green]Yes[/green]" if status.installed else "[red]No[/red]"
        meets = (
            "[green]Yes[/green]"
            if status.meets_minimum
            else "[yellow]No[/yellow]"
        )
        table.add_row(
            status.name,
            installed,
            str(status.version) if status.version else "N/A",
            str(status.minimum_version) if status.minimum_version else "N/A",
            meets,
        )

    console.print(table)


@app.command("install")
def install_tool(
    tool: Annotated[
        str, typer.Argument(help=f"Tool to install ({SUPPORTED_TOOLS}).")
    ],
) -> None:
    """Install a tool using the detected package manager."""
    manager = ToolManager()
    try:
        with console.status(f"[bold green]Installing {tool} ...[/bold green]"):
            result = manager.install(tool)
        if result.ok:
            console.print(f"[green]Successfully installed {tool}.[/green]")
        else:
            console.print(f"[red]Install failed:[/red] {result.stderr}")
            raise typer.Exit(code=1)
    except (ValueError, RuntimeError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command("uninstall")
def uninstall_tool(
    tool: Annotated[
        str, typer.Argument(help=f"Tool to uninstall ({SUPPORTED_TOOLS}).")
    ],
) -> None:
    """Uninstall a tool using the detected package manager."""
    manager = ToolManager()
    try:
        with console.status(f"[bold yellow]Uninstalling {tool} ...[/bold yellow]"):
            result = manager.uninstall(tool)
        if result.ok:
            console.print(f"[green]Successfully uninstalled {tool}.[/green]")
        else:
            console.print(f"[red]Uninstall failed:[/red] {result.stderr}")
            raise typer.Exit(code=1)
    except (ValueError, RuntimeError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command("check")
def check_environment(
    json_output: Annotated[
        bool, typer.Option("--json", "-j", help="Write a JSON report.")
    ] = False,
    output_dir: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Directory for report files."),
    ] = None,
) -> None:
    """Scan the environment and validate eSim readiness."""
    manager = ToolManager()
    scanner = DependencyScanner(tool_manager=manager)
    report = scanner.scan()

    # Render the terminal summary.
    summary = Table(title="eToolManager - Environment Readiness", box=box.ROUNDED)
    summary.add_column("Dependency", style="bold cyan")
    summary.add_column("Status", justify="center")
    summary.add_column("Detail")

    for check in report.checks:
        status_text = "[green]OK[/green]" if check.ok else "[red]MISSING[/red]"
        summary.add_row(check.name, status_text, check.detail)
    console.print(summary)

    if report.ready:
        console.print("\n[bold green]Environment is ready for eSim![/bold green]\n")
    else:
        console.print(
            f"\n[bold red]{report.failed_count} dependency(-ies) missing.[/bold red]"
        )
        if report.fixes:
            console.print("\n[bold yellow]Suggested fixes:[/bold yellow]")
            for idx, fix in enumerate(report.fixes, start=1):
                console.print(f"  {idx}. {fix}")
        console.print()

    if json_output:
        target_dir = output_dir or Path("reports")
        statuses = manager.check_all()
        json_path = generate_json_report(report, target_dir / "report.json", statuses)
        md_path = generate_markdown_report(report, target_dir / "report.md", statuses)
        console.print(f"[green]Reports written:[/green] {json_path}, {md_path}")


@app.command("doctor")
def doctor() -> None:
    """Alias for ``check`` that targets the terminal summary only."""
    check_environment(json_output=False)


def main() -> None:
    """Programmatic entry point used by the console script."""
    app()


if __name__ == "__main__":
    main()