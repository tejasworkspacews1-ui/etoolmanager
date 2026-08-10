# eToolManager - Usage Guide

> **Automated Tool Manager for the eSim Ecosystem**

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Installation](#2-installation)
- [3. Commands](#3-commands)
- [4. Command Reference](#4-command-reference)
- [5. Reports](#5-reports)
- [6. Logging](#6-logging)
- [7. Extending the Tool Registry](#7-extending-the-tool-registry)
- [8. Troubleshooting](#8-troubleshooting)
- [9. Author & Attribution](#9-author--attribution)

---

## 1. Introduction

eToolManager is a command-line tool that automates the management of
external tools required by eSim. It detects your operating system, checks
the installation status of tools like Git, Python, KiCad, and Ngspice,
scans for missing dependencies, and generates detailed reports.

---

## 2. Installation

### Prerequisites

- Python 3.11 or later
- `pip` package manager

### Steps

```bash
# Clone the repository
git clone https://github.com/tejasworkspacews1-ui/etoolmanager.git
cd etoolmanager

# Create a virtual environment
python -m venv .venv

# Activate it
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package (optional)
pip install -e .
```

### Verify the installation

```bash
etoolmanager --help
```

Or without installing:

```bash
python -m etoolmanager --help
```

---

## 3. Commands

eToolManager provides six commands:

| Command | Description |
|---------|-------------|
| `system` | Display detailed OS information |
| `status` | Check tool installation status and version |
| `install` | Install a tool using the package manager |
| `uninstall` | Uninstall a tool |
| `check` | Scan environment and validate eSim readiness |
| `doctor` | Alias for `check` (terminal summary only) |

### Global Option

| Option | Description |
|--------|-------------|
| `--verbose, -v` | Enable DEBUG-level logging |

---

## 4. Command Reference

### `system`

Display the detected operating system, version, architecture, and package
manager.

```bash
etoolmanager system
```

**Example output:**

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

### `status`

Check whether a tool is installed and its version.

```bash
# Single tool
etoolmanager status git

# All supported tools
etoolmanager status
```

**Example output:**

```
┌─ eToolManager - Tool Status ─────────────────────────┐
│ Tool    │ Installed │ Version │ Minimum │ Meets Min │
│---------│-----------│---------│---------│-----------│
│ git     │ Yes       │ 2.43.0  │ 2.25.0  │ Yes       │
│ python  │ Yes       │ 3.11.9  │ 3.11.0  │ Yes       │
│ kicad   │ No        │ N/A     │ 7.0.0   │ No        │
│ ngspice │ No        │ N/A     │ 37.0.0  │ No        │
└──────────────────────────────────────────────────────┘
```

### `install`

Install a tool using the detected package manager.

```bash
etoolmanager install git
```

On Linux/macOS, `sudo` is automatically prepended to the command.

### `uninstall`

Uninstall a tool using the detected package manager.

```bash
etoolmanager uninstall ngspice
```

### `check`

Scan the environment for missing dependencies and validate eSim readiness.

```bash
# Terminal summary only
etoolmanager check

# Generate JSON + Markdown reports
etoolmanager check --json

# Specify output directory
etoolmanager check --json --output reports/
```

**Options:**

| Option | Description |
|--------|-------------|
| `--json, -j` | Write JSON and Markdown report files |
| `--output, -o` | Directory for report files (default: `reports/`) |

### `doctor`

Quick alias for `check` that shows only the terminal summary.

```bash
etoolmanager doctor
```

---

## 5. Reports

When `--json` is passed to `check`, two files are generated:

- `reports/report.md` — human-readable Markdown
- `reports/report.json` — machine-readable JSON

Both include:

- System information
- Installed tools
- Missing dependencies
- Suggested fixes
- Timestamp
- Author attribution

---

## 6. Logging

eToolManager uses structured logging with the following levels:

| Level | Purpose |
|-------|---------|
| `DEBUG` | Detailed diagnostic information (enabled with `--verbose`) |
| `INFO` | Normal operational messages |
| `WARNING` | Potential issues that don't stop execution |
| `ERROR` | Failures that need attention |

Logs are written to:

- **Console** (stdout)
- **File** — timestamped rotating files in `logs/`

Example log entry:

```
2026-08-10 20:00:00 | INFO     | etoolmanager.core.tool_manager | Tool 'git' installed=True binary=git version=2.43.0 meets_min=True
```

---

## 7. Extending the Tool Registry

To add a new tool, edit `etoolmanager/config/tools.yaml`:

```yaml
tools:
  mytool:
    display_name: "My Tool"
    description: "What this tool does for eSim"
    default_version: "1.0.0"
    version_command: ["mytool", "--version"]
    version_regex: "(\\d+\\.\\d+(?:\\.\\d+)?)"
    binary_names: ["mytool"]
    install:
      ubuntu: ["apt-get", "install", "-y", "mytool"]
      debian: ["apt-get", "install", "-y", "mytool"]
      fedora: ["dnf", "install", "-y", "mytool"]
      arch: ["pacman", "-S", "--noconfirm", "mytool"]
      windows: ["winget", "install", "--id", "mytool"]
      macos: ["brew", "install", "mytool"]
    uninstall:
      ubuntu: ["apt-get", "remove", "-y", "mytool"]
      debian: ["apt-get", "remove", "-y", "mytool"]
      fedora: ["dnf", "remove", "-y", "mytool"]
      arch: ["pacman", "-R", "--noconfirm", "mytool"]
      windows: ["winget", "uninstall", "--id", "mytool"]
      macos: ["brew", "uninstall", "mytool"]
    required_for_esim: false
```

No Python code changes are needed unless the tool requires custom install
logic.

---

## 8. Troubleshooting

### `etoolmanager` command not found

Install the package or use `python -m etoolmanager`:

```bash
pip install -e .
# or
python -m etoolmanager --help
```

### `sudo` password prompt during install

The CLI prepends `sudo` on Linux/macOS. This is expected. If you prefer,
run the command as root or remove `sudo` via a custom YAML registry.

### Dependencies reported as missing

Check that the required Python packages are installed:

```bash
pip install numpy scipy matplotlib PyQt5
```

### KiCad / Ngspice not detected

These tools install binaries that may not be on `PATH`. Ensure they are
installed via your package manager and their binaries are accessible.

---

## 9. Author & Attribution

This usage guide was written by **Tejas Kamble** as part of the
**FOSSEE eSim Semester Long Internship – Autumn 2026 (Task 5: Automated
Tool Manager)** submission.

| Field | Value |
|-------|-------|
| **Author** | Tejas Kamble |
| **Email** | [tejasksocials@gmail.com](mailto:tejasksocials@gmail.com) |
| **Phone** | +91 8928545352 |
| **Portfolio** | https://tejas-personal-portfolio-dev.vercel.app/ |
| **LinkedIn** | https://www.linkedin.com/in/tejas-kamble-5342443b1 |
| **GitHub** | https://github.com/tejasworkspacews1-ui |
| **Instagram** | @tejask.co.in |

© 2026 Tejas Kamble · [GitHub](https://github.com/tejasworkspacews1-ui)