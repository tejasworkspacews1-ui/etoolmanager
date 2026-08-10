# eToolManager

> **Automated Tool Manager for the eSim Ecosystem**

![Project Logo](assets/logo.png)

eToolManager is a cross-platform Python application that automates the
installation, detection, configuration, version management, dependency
checking, and status reporting of external tools required by **eSim** — the
open-source EDA tool developed by FOSSEE, IIT Bombay.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [CLI Examples](#cli-examples)
- [Screenshots](#screenshots)
- [Report Samples](#report-samples)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)
- [Author & Attribution](#author--attribution)
- [License](#license)

---

## Project Overview

eSim is an open-source EDA tool used for electronic circuit design and
simulation. It depends on several external tools and libraries — Git,
Python, KiCad, Ngspice, and various Python packages — that must be installed
and correctly configured for eSim to function.

**eToolManager** solves the "dependency hell" problem by providing:

1. **Tool Installation Management** — detect the OS, select the right
   package manager, and install/uninstall tools with a single command.
2. **Dependency Checker** — scan the environment for missing dependencies,
   generate a detailed report, suggest fixes, and validate environment
   readiness.

The project follows clean, modular software engineering practices: SOLID
principles, separation of business logic from the CLI, type hints, docstrings,
and a comprehensive test suite with ~90% coverage.

---

## Features

### OS Detection

Detects and reports:

| OS | Package Manager |
|----|-----------------|
| Ubuntu / Debian | `apt-get` |
| Fedora / RHEL / CentOS | `dnf` |
| Arch / Manjaro | `pacman` |
| Windows | `winget` |
| macOS | `brew` |

Displays: OS name, version, architecture, and package manager.

### Tool Manager

Supports four sample tools:

- **Git**
- **Python**
- **KiCad**
- **Ngspice**

Operations:

- `install` — install a tool using the detected package manager
- `uninstall` — remove a tool
- `version check` — query the installed version
- `status` — check whether a tool is installed and meets the minimum version

### Dependency Scanner

Checks:

- Python version
- `pip` availability
- Git binary
- Required Python packages (numpy, scipy, matplotlib, PyQt5, ...)
- Environment variables (PATH, HOME)
- Missing binaries (KiCad, Ngspice)

Generates:

- Terminal summary (Rich table)
- JSON report (`reports/report.json`)
- Markdown report (`reports/report.md`)

### Report Generation

Each report includes:

- System information
- Installed tools
- Missing dependencies
- Suggested fixes
- Timestamp

### Logging

Structured logging with:

- `INFO`, `WARNING`, `ERROR`, `DEBUG` levels
- Console and rotating-file handlers
- Timestamped log files in `logs/`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLI (typer + rich)                          │
│  system │ status │ install │ uninstall │ check │ doctor             │
└───────────────┬─────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Business Logic (core)                         │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────────────────┐  │
│  │ OS Detector  │   │ ToolManager  │   │ DependencyScanner       │  │
│  └──────┬───────┘   └──────┬───────┘   └──────────┬──────────────┘  │
└─────────┼──────────────────┼──────────────────────┼─────────────────┘
          │                  │                      │
          ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Installers (Strategy pattern)                    │
│  BaseInstaller ◄── PackageManagerInstaller ◄── InstallerFactory     │
└─────────────────────────────────────────────────────────────────────┘
          │                  │                      │
          ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Config (YAML registry)                         │
│  tools.yaml  ──►  ToolConfig  ──►  load_tool_config                 │
└─────────────────────────────────────────────────────────────────────┘
          │                  │                      │
          ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Utilities                                   │
│  subprocess_runner │ version │ logger                                │
└─────────────────────────────────────────────────────────────────────┘
```

### Module Interactions

| Module | Responsibility | Depends On |
|--------|----------------|------------|
| `cli/app.py` | Typer commands, Rich rendering | `core`, `dependency`, `reports` |
| `core/os_detector.py` | OS & package manager detection | `utils/logger` |
| `core/tool_manager.py` | Tool lifecycle facade | `config`, `utils` |
| `installers/*` | Install strategies | `config`, `utils` |
| `dependency/scanner.py` | Environment checks | `core`, `config`, `utils` |
| `reports/generator.py` | JSON/Markdown output | `dependency`, `core` |
| `config/loader.py` | YAML registry loading | `utils/logger` |
| `utils/*` | Subprocess, version, logging | stdlib |

### Data Flow

```
User CLI command
        │
        ▼
ToolManager / DependencyScanner
        │
        ├──► detect_system() ──► SystemInfo
        ├──► load_tool_config() ──► ToolConfig[]
        ├──► run_command() ──► CommandResult
        └──► parse_version() ──► Version
        │
        ▼
DependencyReport / ToolStatus[]
        │
        ├──► generate_json_report() ──► reports/report.json
        └──► generate_markdown_report() ──► reports/report.md
```

### Class Responsibilities

| Class | Responsibility |
|-------|----------------|
| `SystemInfo` | Immutable OS snapshot (name, version, arch, pkg manager) |
| `ToolConfig` | Immutable tool registry entry |
| `ToolStatus` | Per-tool detection result |
| `ToolManager` | Facade for install/uninstall/status/version |
| `BaseInstaller` | Abstract installer interface (Strategy) |
| `PackageManagerInstaller` | Concrete package-manager installer |
| `InstallerFactory` | Selects the right installer strategy |
| `DependencyCheck` | Single dependency check result |
| `DependencyReport` | Aggregated readiness report |
| `DependencyScanner` | Runs all checks, aggregates fixes |
| `CommandResult` | Standardised subprocess result |

---

## Installation

### Prerequisites

- Python 3.11 or later
- `pip`

### Install from source

```bash
# 1. Clone the repository
git clone https://github.com/tejasworkspacews1-ui/etoolmanager.git
cd etoolmanager

# 2. (Recommended) Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install the package (optional, gives you the `etoolmanager` command)
pip install -e .
```

### Run without installing

```bash
python -m etoolmanager --help
```

---

## Usage

```
Usage: etoolmanager [OPTIONS] COMMAND [ARGS]...

  Automated tool manager for the eSim ecosystem.

Options:
  --verbose, -v   Enable DEBUG logging.
  --help          Show this message and exit.

Commands:
  check      Scan the environment and validate eSim readiness.
  doctor     Alias for check that targets the terminal summary only.
  install    Install a tool using the detected package manager.
  status     Check whether a tool is installed and its version.
  system     Display detailed information about the detected operating system.
  uninstall  Uninstall a tool using the detected package manager.
```

---

## CLI Examples

### Display system information

```bash
etoolmanager system
```

```
┌─ System ─────────────────────────────────────────────┐
│ eToolManager - System Information                    │
│                                                      │
│ OS: Windows 11 (windows)                             │
│ Version: 10.0.22631                                  │
│ Architecture: AMD64                                  │
│ Package Manager: winget                              │
│ Python: 3.11.9                                       │
└──────────────────────────────────────────────────────┘
```

### Check tool status

```bash
# Single tool
etoolmanager status git

# All tools
etoolmanager status
```

### Install a tool

```bash
etoolmanager install git
```

### Uninstall a tool

```bash
etoolmanager uninstall ngspice
```

### Check environment readiness

```bash
# Terminal summary only
etoolmanager check

# Generate JSON + Markdown reports
etoolmanager check --json --output reports/
```

### Quick doctor

```bash
etoolmanager doctor
```

---

## Screenshots

> **Note:** Screenshots are placeholders. Replace with actual captures of
> your terminal output.

| Command | Screenshot |
|---------|------------|
| `etoolmanager system` | ![system](assets/screenshots/system.png) |
| `etoolmanager status` | ![status](assets/screenshots/status.png) |
| `etoolmanager check` | ![check](assets/screenshots/check.png) |
| `etoolmanager install git` | ![install](assets/screenshots/install.png) |

---

## Report Samples

### Markdown Report (`reports/report.md`)

```markdown
# eToolManager - Environment Readiness Report

**Timestamp:** 2026-08-10T20:00:00

## System Information

- **OS:** Ubuntu 22.04 (`ubuntu`)
- **Version:** 22.04
- **Architecture:** x86_64
- **Package Manager:** apt-get
- **Python:** 3.11.9

## Summary

- **Ready:** ❌ No
- **Checks Passed:** 9 / 12
- **Checks Failed:** 3

## Installed Tools

| Tool | Installed | Version | Minimum | Meets Minimum |
|------|-----------|---------|---------|---------------|
| git | Yes | 2.43.0 | 2.25.0 | Yes |
| python | Yes | 3.11.9 | 3.11.0 | Yes |
| kicad | No | N/A | 7.0.0 | No |
| ngspice | No | N/A | 37.0.0 | No |

## Dependency Checks

| Category | Dependency | Status | Detail |
|----------|------------|--------|--------|
| python_version | Python version | ✅ | Detected 3.11.9, required >= 3.8.0 |
| pip | pip | ✅ | pip found on PATH |
| git | Git | ✅ | Installed: 2.43.0 |
| package | numpy | ✅ | 1.26.4 |
| ... | ... | ... | ... |
| binary | kicad | ❌ | Not installed |
| binary | ngspice | ❌ | Not installed |

## Missing Dependencies

- **kicad** (binary): Not installed
- **ngspice** (binary): Not installed

## Suggested Fixes

1. Install the kicad package using your package manager
2. Install the ngspice package using your package manager

---

## Author & Attribution

...
```

### JSON Report (`reports/report.json`)

```json
{
  "timestamp": "2026-08-10T20:00:00",
  "system": {
    "os_name": "ubuntu",
    "os_display": "Ubuntu 22.04",
    "version": "22.04",
    "architecture": "x86_64",
    "package_manager": "apt-get",
    "python_version": "3.11.9"
  },
  "ready": false,
  "summary": {
    "total": 12,
    "passed": 9,
    "failed": 3
  },
  "checks": [
    {
      "category": "python_version",
      "name": "Python version",
      "ok": true,
      "detail": "Detected 3.11.9, required >= 3.8.0",
      "fix": null
    }
  ],
  "missing": [],
  "suggested_fixes": [
    "Install the kicad package using your package manager"
  ]
}
```

---

## Testing

The test suite covers:

- OS detection
- Version parsing
- Dependency detection
- Report generation
- Tool manager lifecycle
- Installer strategies
- CLI commands
- Logging configuration

```bash
# Run the full test suite with coverage
pytest

# Run a single test module
pytest etoolmanager/tests/test_version.py

# Generate an HTML coverage report
pytest --cov=etoolmanager --cov-report=html
```

**Current coverage: ~90%** (target: 80%+).

---

## Project Structure

```
etoolmanager/
├── cli/                  # Typer commands and Rich rendering
│   ├── __init__.py
│   └── app.py
├── core/                 # Business logic
│   ├── __init__.py
│   ├── os_detector.py    # OS & package manager detection
│   └── tool_manager.py   # Tool lifecycle facade
├── installers/           # Install strategies (Strategy pattern)
│   ├── __init__.py
│   ├── base.py           # Abstract interface
│   ├── factory.py        # Strategy selection
│   └── package_manager.py# Concrete package-manager installer
├── dependency/           # Dependency scanning
│   ├── __init__.py
│   └── scanner.py        # Checks, report model, aggregation
├── config/               # Configuration
│   ├── __init__.py
│   ├── loader.py         # YAML registry loader
│   └── tools.yaml        # Declarative tool registry
├── utils/                # Utilities
│   ├── __init__.py
│   ├── logger.py         # Structured logging
│   ├── subprocess_runner.py
│   └── version.py        # Version parsing/comparison
├── reports/              # Report generation
│   ├── __init__.py
│   └── generator.py      # JSON + Markdown writers
├── tests/                # pytest test suite
├── docs/                 # Documentation
├── assets/               # Logos, screenshots
├── README.md
├── requirements.txt
├── pyproject.toml
└── .gitignore
```

---

## Future Improvements

- **GUI frontend** built on the same business logic (e.g. PyQt5/Tkinter).
- **Configurable tool registry** via user-provided YAML files.
- **Package manager detection** using `shutil.which` for the actual
  package manager binary, not just the OS mapping.
- **Version range support** (e.g. `>=2.25, <3.0`) instead of a single
  minimum.
- **Offline / cache-aware installs** for corporate environments.
- **CI/CD pipeline** with GitHub Actions to run tests on Ubuntu, Windows,
  and macOS.
- **REST API** wrapper exposing the same operations.
- **Plugin system** for custom installers and checkers.

---

## Author & Attribution

This project was designed and implemented by **Tejas Kamble** as a
submission prototype for the **FOSSEE eSim Semester Long Internship –
Autumn 2026 (Task 5: Automated Tool Manager)**.

| Field | Value |
|-------|-------|
| **Author** | Tejas Kamble |
| **Email** | [tejasksocials@gmail.com](mailto:tejasksocials@gmail.com) |
| **Phone** | +91 8928545352 |
| **Portfolio** | https://tejas-personal-portfolio-dev.vercel.app/ |
| **LinkedIn** | https://www.linkedin.com/in/tejas-kamble-5342443b1 |
| **GitHub** | https://github.com/tejasworkspacews1-ui |
| **Instagram** | @tejask.co.in |

### Attribution Statement

The original code, architecture, documentation, and implementation in this
repository are the work of **Tejas Kamble**. This project is **not** a
claim of ownership over:

- The **FOSSEE Project** or the **eSim** application
- **KiCad**, **Ngspice**, or any other third-party software
- Any external open-source projects or dependencies referenced

All third-party software and dependencies remain the property of their
respective owners and are used under their respective licenses. This
project is an independent implementation for evaluation purposes.

### Footer

© 2026 Tejas Kamble · Built for the FOSSEE eSim Semester Long Internship –
Autumn 2026 · [GitHub](https://github.com/tejasworkspacews1-ui)

---

## License

This project is licensed under the [MIT License](LICENSE).