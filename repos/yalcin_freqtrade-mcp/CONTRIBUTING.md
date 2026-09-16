# Contributing to freqtrade-mcp

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. Fork and clone the repository:

```bash
git clone https://github.com/your-username/freqtrade-mcp.git
cd freqtrade-mcp
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

3. Install pre-commit hooks:

```bash
pre-commit install
```

## Code Standards

- **Python >= 3.13** — use modern syntax features
- **Type hints** on all functions — enforced by mypy strict mode
- **Google-style docstrings** on all public functions, classes, and methods
- **Ruff** for linting and formatting (line length: 99)
- **No eval/exec** — use `inspect` and `ast` modules only
- **Input validation** — all external inputs must pass through `validators.py`
- **Read-only** — never add functionality that modifies state or connects to exchanges

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=freqtrade_mcp --cov-report=term-missing

# Run a specific test file
pytest tests/test_validators.py

# Run a specific test
pytest tests/test_validators.py::TestValidateIdentifier::test_valid_identifiers
```

## Linting and Type Checking

```bash
# Lint
ruff check src/ tests/

# Auto-fix lint issues
ruff check --fix src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Ensure all checks pass: `ruff check`, `ruff format --check`, `mypy src/`, `pytest`
4. Update `CHANGELOG.md` with your changes
5. Submit a pull request

## Reporting Issues

- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) for bugs
- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) for new features

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
