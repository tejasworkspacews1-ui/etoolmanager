# eToolManager - 5-Minute Explanation Script

> **FOSSEE eSim Semester Long Internship – Autumn 2026 (Task 5: Automated Tool Manager)**

This script is designed to help you confidently explain every part of the
eToolManager project in a 5-minute presentation or interview.

---

## Script

### 0:00 - Introduction (30 seconds)

> "Hello, I'm Tejas Kamble. This is **eToolManager**, my submission for
> Task 5 of the FOSSEE eSim Semester Long Internship. eToolManager is a
> cross-platform Python application that automates the installation,
> detection, configuration, version management, dependency checking, and
> status reporting of external tools required by eSim.
>
> The problem it solves is simple: eSim depends on Git, Python, KiCad,
> Ngspice, and several Python packages. Setting these up manually across
> different operating systems is error-prone. eToolManager automates this
> with a clean, modular, testable architecture."

### 0:30 - Architecture Overview (1 minute)

> "The project follows a layered architecture with five layers:
>
> 1. **CLI layer** (`cli/`) — Typer commands with Rich rendering. This is
>    the only user-facing component.
> 2. **Business logic layer** (`core/`) — `ToolManager` is a facade that
>    handles tool lifecycle, and `os_detector` detects the operating system.
> 3. **Strategy layer** (`installers/`) — `BaseInstaller` is an abstract
>    interface, `PackageManagerInstaller` is the concrete implementation,
>    and `InstallerFactory` selects the right strategy.
> 4. **Configuration layer** (`config/`) — A declarative YAML registry
>    (`tools.yaml`) defines every tool and its platform-specific commands.
> 5. **Utility layer** (`utils/`) — Safe subprocess wrapper, version
>    parsing, and structured logging.
>
> The key design decision is **separation of concerns**: the CLI never
> talks to subprocess directly. It delegates to `ToolManager`, which uses
> the YAML registry and the subprocess runner. This makes the code
> testable and reusable."

### 1:30 - OS Detection (45 seconds)

> "The OS detector uses Python's `platform` module and, on Linux, parses
> `/etc/os-release` to identify the distribution. It maps each OS to its
> package manager:
>
> - Ubuntu/Debian → `apt-get`
> - Fedora → `dnf`
> - Arch → `pacman`
> - Windows → `winget`
> - macOS → `brew`
>
> The result is an immutable `SystemInfo` dataclass that carries the OS
> name, display name, version, architecture, package manager, and Python
> version. This is used everywhere downstream — the tool manager, the
> dependency scanner, and the reports."

### 2:15 - Tool Manager (1 minute)

> "The `ToolManager` is the heart of the application. It supports four
> tools: Git, Python, KiCad, and Ngspice. For each tool, it can:
>
> - **Check status** — find the binary on PATH, run the version command,
>   parse the version, and compare it against a minimum.
> - **Install** — resolve the platform-specific command from the YAML
>   registry and run it, prepending `sudo` on POSIX systems.
> - **Uninstall** — same approach with the uninstall command.
>
> The tool definitions live in `config/tools.yaml`. Adding a new tool is
> just adding a YAML block — no Python code changes needed. This is the
> Open/Closed principle in action."

### 3:15 - Dependency Scanner (1 minute)

> "The `DependencyScanner` checks six categories:
>
> 1. Python version — must be at least 3.8.
> 2. pip availability.
> 3. Git binary.
> 4. Required Python packages — numpy, scipy, matplotlib, PyQt5, and more.
> 5. Environment variables — PATH and HOME.
> 6. Missing binaries — KiCad and Ngspice.
>
> Each check produces a `DependencyCheck` with a category, name, pass/fail
> flag, detail, and a suggested fix. The scanner aggregates these into a
> `DependencyReport` with a readiness flag and unique suggested fixes.
>
> The report can be rendered as a Rich table in the terminal, or written
> to `reports/report.json` and `reports/report.md` for sharing."

### 4:15 - Testing & Quality (45 seconds)

> "The project has **98 test cases** with **~90% coverage**, exceeding the
> 80% target. Tests cover:
>
> - OS detection
> - Version parsing and comparison
> - Tool manager lifecycle
> - Installer strategies
> - Dependency scanner
> - Report generation
> - CLI commands via Typer's CliRunner
> - Logging and subprocess wrapper
>
> Every function has type hints and docstrings. The code follows SOLID
> principles — the installer strategy pattern, the facade pattern, and
> dependency inversion are all applied."

### 5:00 - Closing (30 seconds)

> "In summary, eToolManager is a production-quality, cross-platform tool
> manager that solves a real problem for the eSim ecosystem. It's modular,
> testable, documented, and follows professional software engineering
> practices. Thank you for your time."

---

## Key Talking Points

| Topic | Key Point |
|-------|-----------|
| Architecture | Layered: CLI → Business Logic → Strategy → Config → Utils |
| Design Pattern | Facade (`ToolManager`), Strategy (`BaseInstaller`), Factory (`InstallerFactory`) |
| Config | Declarative YAML registry — add tools without code changes |
| SOLID | Open/Closed (YAML tools), Dependency Inversion (abstractions) |
| Testing | 98 tests, ~90% coverage |
| Cross-platform | Ubuntu, Debian, Fedora, Arch, Windows, macOS |

---

## Author & Attribution

This explanation script was written by **Tejas Kamble** as part of the
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