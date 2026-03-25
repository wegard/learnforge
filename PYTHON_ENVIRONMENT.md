# Python Environment

LearnForge uses a single `pyproject.toml` as the source of truth for all
Python packaging, dependencies, and tool configuration. The environment
can run either inside a local micromamba prefix or directly on a system
Python — the `scripts/run-in-env.sh` wrapper handles both transparently.

## Requirements

- Python 3.13+
- pip (bundled with Python)
- micromamba (optional, for isolated environments)

## Quick Start

### Option A: micromamba (recommended for full isolation)

```bash
make mamba-bootstrap   # creates .micromamba/ prefix, installs everything
make test              # runs through the prefix automatically
```

`bootstrap_micromamba.sh` creates a local prefix at `.micromamba/`,
installs Python 3.13 from conda-forge, pip-installs the project in
editable mode with dev extras, and sets up pre-commit hooks.

### Option B: system / venv Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

When no `.micromamba/conda-meta/` directory exists, `run-in-env.sh`
falls through to the ambient Python — so `make test` works in both
setups without configuration.

## Project Layout

```
pyproject.toml          # Package metadata, dependencies, tool config
environment.yml         # Minimal conda spec (Python + pip only)
Makefile                # Convenience targets wrapping run-in-env.sh
scripts/
  run-in-env.sh         # Transparent env wrapper (micromamba or passthrough)
  bootstrap_micromamba.sh  # One-shot micromamba setup
  bootstrap.sh          # pip install + pre-commit + validate
.pre-commit-config.yaml # YAML checks, ruff lint + format
```

## Dependencies

### Runtime

| Package   | Version        | Purpose                          |
|-----------|----------------|----------------------------------|
| Jinja2    | >=3.1.4        | Template scaffolding             |
| Pydantic  | >=2.11, <3     | Schema validation for meta.yml   |
| PyYAML    | >=6.0.2        | YAML parsing                     |
| Textual   | >=1.0, <2      | Terminal dashboard (`teach tui`)  |
| Typer     | >=0.16, <1     | CLI framework (`teach` command)  |

### Dev-only (`pip install -e ".[dev]"`)

| Package     | Version  | Purpose              |
|-------------|----------|----------------------|
| pre-commit  | >=4.1    | Git hook management  |
| pytest      | >=8.3    | Test runner          |
| ruff        | >=0.11   | Linter + formatter   |

## How `run-in-env.sh` Works

```
run-in-env.sh <command> [args...]
```

1. If `.micromamba/conda-meta/` exists → runs the command via
   `micromamba run -p .micromamba/ <command>`.
2. Otherwise → runs `<command>` directly (assumes ambient Python has
   the project installed).

All Makefile targets and helper scripts use this wrapper, so the
environment is resolved consistently regardless of how it was set up.

## Makefile Targets

| Target           | What it does                         |
|------------------|--------------------------------------|
| `make install`   | `pip install -e ".[dev]"`            |
| `make lint`      | `ruff check app tests`               |
| `make test`      | `pytest -q`                          |
| `make validate`  | `teach validate`                     |
| `make build-samples` | Build all representative targets |
| `make mamba-bootstrap` | Create micromamba environment   |

## Ruff Configuration

Configured in `pyproject.toml` under `[tool.ruff]`:

- Line length: 100
- Target: Python 3.13
- Enabled rule sets: `E` (pycodestyle), `F` (pyflakes), `I` (isort),
  `UP` (pyupgrade), `B` (flake8-bugbear)
- Pre-commit runs both `ruff` (lint) and `ruff-format` (formatting)

## Environment Variables

| Variable                  | Default          | Purpose                         |
|---------------------------|------------------|---------------------------------|
| `LEARNFORGE_ENV_PREFIX`   | `.micromamba`    | Micromamba prefix path          |
| `LEARNFORGE_XDG_CACHE_HOME` | `.cache`      | Cache directory for micromamba  |
| `EDITOR`                  | `nvim`           | Editor for `teach tui` / `teach open` |
