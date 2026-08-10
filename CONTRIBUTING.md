# Contributing to eToolManager

> **Automated Tool Manager for the eSim Ecosystem**

First off, thank you for considering contributing to eToolManager! This
project was developed by **Tejas Kamble** as a submission prototype for the
FOSSEE eSim Semester Long Internship – Autumn 2026 (Task 5: Automated Tool
Manager).

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Author & Attribution](#author--attribution)

---

## Code of Conduct

Be respectful, inclusive, and constructive. Harassment or discrimination
of any kind will not be tolerated.

---

## How to Contribute

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally.
3. Create a **feature branch**.
4. Make your changes.
5. **Test** your changes.
6. **Commit** with a clear message.
7. **Push** to your fork.
8. Open a **Pull Request**.

---

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/etoolmanager.git
cd etoolmanager

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install the package in editable mode
pip install -e .
```

---

## Coding Standards

- **Python 3.11+** — use modern type hints (`list[str]`, `dict[str, Any]`).
- **Type hints** — every function signature must be annotated.
- **Docstrings** — every public function/class must have a docstring
  describing its purpose, parameters, and return value.
- **Line length** — keep lines under 88 characters where practical.
- **Imports** — group standard library, third-party, and local imports.
- **Naming** — use `snake_case` for functions/variables, `PascalCase` for
  classes, `UPPER_CASE` for constants.
- **Error handling** — raise clear exceptions with descriptive messages.
- **No side effects at import time** — keep module-level code minimal.

### File Header

Every new Python file must include the project header block:

```python
# =============================================================================
# Project      : eToolManager
# File         : <path>
# Purpose      : <brief description>
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
```

---

## Testing

All changes must pass the existing test suite and maintain at least 80%
coverage.

```bash
# Run the full test suite with coverage
pytest

# Run a single test module
pytest etoolmanager/tests/test_version.py

# Run tests without coverage
pytest --no-cov
```

### Writing Tests

- Place tests in `etoolmanager/tests/`.
- Name test files `test_<module>.py`.
- Name test methods `test_<behaviour>`.
- Use `pytest` fixtures from `conftest.py` where possible.
- Mock external subprocess calls with `unittest.mock.patch`.

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/)
specification:

```
<type>(<scope>): <description>

[optional body]
```

**Types:**

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

**Examples:**

```
feat(core): add version comparison operators
fix(cli): handle unknown tool names gracefully
docs(readme): add architecture diagram
test(dependency): add scanner unit tests
```

---

## Pull Request Process

1. Ensure your branch is up to date with `main`.
2. Run the full test suite and confirm coverage >= 80%.
3. Update documentation if your change affects usage.
4. Add a CHANGELOG entry under `[Unreleased]`.
5. Open the PR with a clear title and description.
6. Reference any related issues.

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

© 2026 Tejas Kamble · [GitHub](https://github.com/tejasworkspacews1-ui)