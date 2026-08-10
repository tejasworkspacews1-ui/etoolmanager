# Changelog

All notable changes to **eToolManager** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Initial project scaffolding (pyproject.toml, requirements.txt, .gitignore)

---

## [1.0.0] - 2026-08-10

### Added

#### Core

- **OS Detection** (`core/os_detector.py`):
  - Detect Ubuntu/Debian, Fedora, Arch, Windows, and macOS.
  - Parse `/etc/os-release` on Linux for distribution identification.
  - Map each OS to its package manager (`apt-get`, `dnf`, `pacman`, `winget`, `brew`).
  - `SystemInfo` dataclass with `to_dict()` for reports.
  - `is_windows()`, `is_macos()`, `is_linux()` helpers.

- **Tool Manager** (`core/tool_manager.py`):
  - `ToolStatus` dataclass capturing installed flag, version, minimum version,
    and meets-minimum comparison.
  - `ToolManager` facade with `check_status()`, `check_all()`, `install()`,
    and `uninstall()`.
  - Version detection using per-tool commands from the YAML registry.
  - Automatic `sudo` prefixing on POSIX systems for install/uninstall.

#### Installers

- `BaseInstaller` abstract interface (Strategy pattern).
- `PackageManagerInstaller` concrete implementation.
- `InstallerFactory` for strategy selection.

#### Configuration

- Declarative YAML tool registry (`config/tools.yaml`) covering Git, Python,
  KiCad, and Ngspice.
- `ToolConfig` dataclass and `load_tool_config()` with validation and caching.

#### Dependency Scanner

- `DependencyCheck` and `DependencyReport` dataclasses.
- `DependencyScanner` checks:
  - Python version
  - pip availability
  - Git binary
  - Required Python packages (numpy, scipy, matplotlib, PyQt5, kiwisolver,
    sympy, requests)
  - Environment variables (PATH, HOME)
  - Missing binaries (KiCad, Ngspice)
- Suggested fixes for every missing dependency.
- Overall environment readiness flag.

#### Reports

- `generate_json_report()` — pretty-printed JSON with system info, checks,
  missing dependencies, fixes, timestamp, and author attribution.
- `generate_markdown_report()` — human-readable Markdown with the same data
  in tables and sections.

#### CLI

- Typer-based CLI (`cli/app.py`) with Rich rendering:
  - `system` — display OS information
  - `status` — check tool installation status
  - `install` / `uninstall` — manage tools
  - `check` / `doctor` — scan environment and generate reports
  - `--verbose` global flag for DEBUG logging
- `python -m etoolmanager` entry point.

#### Utilities

- `subprocess_runner.py`:
  - `run_command()` with timeout, output capture, and `check` mode.
  - `which()` and `command_exists()` executable lookup.
  - `CommandResult` dataclass.
- `version.py`:
  - `Version` dataclass with comparison operators.
  - `parse_version()` and `version_meets_minimum()`.
- `logger.py`:
  - Structured logging to console and rotating file.
  - `get_logger()` helper for module-scoped loggers.

#### Testing

- 98 test cases covering:
  - OS detection
  - Version parsing/comparison
  - Tool manager lifecycle
  - Installer strategies and factory
  - Dependency scanner
  - Report generation (JSON + Markdown)
  - CLI commands via Typer `CliRunner`
  - Logging configuration
  - Subprocess wrapper
- Test coverage: **~90%** (target: 80%+).

#### Documentation

- `README.md` with project overview, features, architecture, installation,
  usage, CLI examples, screenshots placeholders, report samples, testing,
  project structure, and future improvements.
- `docs/architecture.md` with component diagram, module interactions, data
  flow, class responsibilities, design decisions, and SOLID analysis.
- `docs/usage.md` with detailed command reference and troubleshooting.
- `CONTRIBUTING.md` with coding standards and PR process.
- `LICENSE` (MIT).
- `CHANGELOG.md`.

---

[Unreleased]: https://github.com/tejasworkspacews1-ui/etoolmanager/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/tejasworkspacews1-ui/etoolmanager/releases/tag/v1.0.0