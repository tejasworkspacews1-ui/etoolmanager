# eToolManager - Design Document

> **Automated Tool Manager for the eSim Ecosystem**

---

## Table of Contents

- [1. Problem Statement](#1-problem-statement)
- [2. Goals & Non-Goals](#2-goals--non-goals)
- [3. Design Overview](#3-design-overview)
- [4. Detailed Design](#4-detailed-design)
- [5. Data Models](#5-data-models)
- [6. Error Handling](#6-error-handling)
- [7. Security Considerations](#7-security-considerations)
- [8. Performance](#8-performance)
- [9. Author & Attribution](#9-author--attribution)

---

## 1. Problem Statement

eSim, the open-source EDA tool from FOSSEE IIT Bombay, depends on several
external tools and libraries:

- **Git** — version control for projects
- **Python** — the core engine language
- **KiCad** — schematic capture and PCB layout
- **Ngspice** — circuit simulation engine
- **Python packages** — numpy, scipy, matplotlib, PyQt5, etc.

Setting up these dependencies manually is:

- **Error-prone** — different OSes use different package managers
- **Time-consuming** — each tool needs separate installation steps
- **Hard to verify** — no easy way to confirm versions meet requirements
- **Fragile** — missing dependencies cause cryptic runtime errors

**eToolManager** solves this by providing a single, cross-platform CLI
that automates installation, detection, configuration, version management,
dependency checking, and status reporting.

---

## 2. Goals & Non-Goals

### Goals

1. Detect the operating system and select the correct package manager.
2. Install, uninstall, and check the status of Git, Python, KiCad, and
   Ngspice.
3. Scan the environment for missing dependencies and suggest fixes.
4. Generate JSON and Markdown reports.
5. Provide structured logging.
6. Achieve at least 80% test coverage.
7. Follow SOLID principles and clean architecture.

### Non-Goals

1. **Not** a replacement for eSim itself.
2. **Not** a full package manager — it delegates to `apt`, `dnf`, `pacman`,
   `winget`, and `brew`.
3. **Not** a GUI application (though the architecture supports one).
4. **Not** a build system for eSim.

---

## 3. Design Overview

The system uses a **layered architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer (CLI)                 │
│            typer commands + rich rendering                   │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                      │
│          ToolManager, DependencyScanner, OSDetector          │
├─────────────────────────────────────────────────────────────┤
│                    Strategy Layer                            │
│          BaseInstaller / PackageManagerInstaller             │
├─────────────────────────────────────────────────────────────┤
│                    Configuration Layer                       │
│            tools.yaml registry + ToolConfig                  │
├─────────────────────────────────────────────────────────────┤
│                    Utility Layer                             │
│        subprocess_runner, version, logger                    │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

| Pattern | Application |
|---------|-------------|
| **Facade** | `ToolManager` hides OS detection, command resolution, subprocess, and version parsing from the CLI. |
| **Strategy** | `BaseInstaller` interface with `PackageManagerInstaller` implementation. |
| **Factory Method** | `InstallerFactory` selects the right installer strategy. |
| **Data Transfer Object** | `SystemInfo`, `ToolStatus`, `DependencyReport` carry data between layers. |
| **Registry** | `tools.yaml` is a declarative registry of supported tools. |

---

## 4. Detailed Design

### 4.1 OS Detection (`core/os_detector.py`)

**Input:** None (uses `platform` module and `/etc/os-release`).

**Output:** `SystemInfo` dataclass.

**Logic:**

1. Call `platform.system()` to get the base OS.
2. On Linux, parse `/etc/os-release` for `ID` and `PRETTY_NAME`.
3. Map the OS to a canonical key (`ubuntu`, `debian`, `fedora`, `arch`,
   `windows`, `macos`).
4. Map the OS to its package manager.
5. Capture architecture and Python version.

**Design decision:** The OS key is canonical and used throughout the
system. The YAML registry uses these keys to select install commands.

### 4.2 Tool Manager (`core/tool_manager.py`)

**Input:** Tool name.

**Output:** `ToolStatus` or `CommandResult`.

**Logic:**

1. Look up the tool in the YAML registry.
2. Find the binary on PATH using `shutil.which`.
3. Run the version command and parse the output.
4. Compare against the minimum version.
5. For install/uninstall, resolve the platform command and run it.

**Design decision:** `ToolManager` is a facade. It does not know about
Typer, Rich, or the CLI. It only knows about tools, commands, and versions.

### 4.3 Installers (`installers/`)

**Input:** `ToolConfig` + platform key.

**Output:** `CommandResult`.

**Logic:**

1. `InstallerFactory.create()` validates the platform key.
2. Returns a `PackageManagerInstaller`.
3. `install()`/`uninstall()` resolve the command from the registry and
   run it, prepending `sudo` on POSIX.

**Design decision:** The Strategy pattern allows future installers (e.g.
AppImage, tarball) without changing callers.

### 4.4 Dependency Scanner (`dependency/scanner.py`)

**Input:** None (uses system + tool manager).

**Output:** `DependencyReport`.

**Logic:**

1. Check Python version.
2. Check pip.
3. Check Git.
4. Check required Python packages.
5. Check environment variables.
6. Check missing binaries (KiCad, Ngspice).
7. Aggregate missing checks and unique fixes.
8. Compute readiness flag.

**Design decision:** Each check is a separate method, making the scanner
easy to extend and test.

### 4.5 Reports (`reports/generator.py`)

**Input:** `DependencyReport` + optional `ToolStatus[]`.

**Output:** JSON and Markdown files.

**Logic:**

1. Build a flat payload dictionary.
2. Serialise to JSON with `json.dumps(indent=2)`.
3. Build Markdown with tables and sections.

**Design decision:** Reports include author attribution to satisfy the
submission requirements.

### 4.6 CLI (`cli/app.py`)

**Input:** User commands.

**Output:** Rich-rendered terminal output.

**Logic:**

1. Parse commands with Typer.
2. Delegate to `ToolManager` / `DependencyScanner`.
3. Render results with Rich tables and panels.

**Design decision:** The CLI is a thin presentation layer. All business
logic lives in the core modules.

---

## 5. Data Models

### `SystemInfo`

```python
@dataclass(frozen=True)
class SystemInfo:
    os_name: str          # "ubuntu", "windows", ...
    os_display: str       # "Ubuntu 22.04"
    version: str          # "22.04"
    architecture: str     # "x86_64"
    package_manager: str  # "apt-get"
    python_version: str   # "3.11.9"
```

### `ToolConfig`

```python
@dataclass(frozen=True)
class ToolConfig:
    name: str
    display_name: str
    description: str
    default_version: str
    version_command: list[str]
    version_regex: str
    binary_names: list[str]
    install: dict[str, list[str]]
    uninstall: dict[str, list[str]]
    required_for_esim: bool
```

### `ToolStatus`

```python
@dataclass
class ToolStatus:
    name: str
    installed: bool
    version: Version | None
    minimum_version: Version | None
    meets_minimum: bool
    command_used: str | None
    error: str | None
```

### `DependencyCheck`

```python
@dataclass
class DependencyCheck:
    category: str   # "python_version", "binary", ...
    name: str       # "Python version", "kicad", ...
    ok: bool
    detail: str
    fix: str | None
```

### `DependencyReport`

```python
@dataclass
class DependencyReport:
    timestamp: str
    system: SystemInfo
    checks: list[DependencyCheck]
    missing: list[DependencyCheck]
    fixes: list[str]
    ready: bool
```

### `CommandResult`

```python
@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    command: list[str]
```

---

## 6. Error Handling

| Scenario | Handling |
|----------|----------|
| Unknown tool name | `ValueError` raised by `ToolManager` |
| Unsupported platform | `RuntimeError` from installer |
| Command timeout | `RuntimeError` from `run_command` |
| Executable not found | `FileNotFoundError` propagates |
| Missing YAML keys | `ValueError` from `_parse_tool` |
| Malformed YAML | `yaml.YAMLError` propagates |
| CLI errors | Typer `Exit(code=1)` with Rich error message |

---

## 7. Security Considerations

1. **No secrets stored** — the tool only runs package-manager commands.
2. **Command injection** — commands come from the bundled YAML registry,
   not from user input. Tool names are validated against the registry.
3. **`sudo` usage** — prepended only on POSIX for install/uninstall.
   Users are prompted for their password by the OS.
4. **Timeout enforcement** — all subprocess calls have a 60-second default
   timeout (300s for installs) to prevent hangs.

---

## 8. Performance

- **YAML registry** is loaded once and cached with `@lru_cache`.
- **Subprocess calls** are minimal — one per version check.
- **Reports** are written with a single `write_text()` call.
- **Logging** uses rotating file handlers to prevent unbounded growth.

---

## 9. Author & Attribution

This design document was written by **Tejas Kamble** as part of the
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

### Attribution Statement

The original code, architecture, documentation, and implementation in this
repository are the work of **Tejas Kamble**. This project is **not** a
claim of ownership over the FOSSEE Project, eSim, KiCad, Ngspice, or any
third-party software.

© 2026 Tejas Kamble · [GitHub](https://github.com/tejasworkspacews1-ui)