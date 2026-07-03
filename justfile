set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]
import 'scripts/just/fleet.just'

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# ── Quality ───────────────────────────────────────────────────────────────────

# Ruff lint (Python) + Biome CI check (webapp)
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome ci .

# Ruff fix + format (Python) + Biome format (webapp)
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome check --write .

# Quick ruff check only (fast feedback loop)
ruff-check:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .

# ── Testing ───────────────────────────────────────────────────────────────────

# Run all unit tests
test:
    uv run pytest tests/unit/ -v --timeout=30

# Run unit tests + coverage report
test-cov:
    uv run pytest tests/unit/ -v --timeout=30 --cov=src/davinci_resolve_mcp --cov-report=term-missing

# Run new extended tests (markers, keyframes, subtitles)
test-ext:
    uv run pytest tests/unit/tools/test_timeline_extended.py tests/unit/tools/test_subtitle_tools.py -v --timeout=30

# Run all tests (unit + integration, needs Resolve running for integration)
test-all:
    uv run pytest tests/ -v --timeout=30

# Run with verbose output and no capture
test-debug:
    uv run pytest tests/unit/ -vvs --timeout=30

# ── Security ──────────────────────────────────────────────────────────────────

# Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Safety dependency audit
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run pip-audit

# ── Development ───────────────────────────────────────────────────────────────

# Install dependencies (production)
install:
    uv sync

# Install with dev dependencies
install-dev:
    uv sync --all-extras

# Update lockfile
lock:
    uv lock

# Type check with mypy
typecheck:
    uv run mypy src/davinci_resolve_mcp --ignore-missing-imports

# ── Run Modes ─────────────────────────────────────────────────────────────────

# Run MCP server (stdio — for Claude Desktop / Cursor)
run:
    uv run davinci-resolve-mcp

# Run MCP server explicitly (stdio)
mcp:
    uv run davinci-resolve-mcp mcp

# Run webapp API backend (port 10843)
web:
    uv run davinci-resolve-mcp web

# Run HTTP MCP server (port 8000)
start:
    uv run davinci-resolve-mcp start

# Check Resolve environment
check:
    uv run davinci-resolve-mcp check

# ── CLI Direct ────────────────────────────────────────────────────────────────

# Open a project (create if needed)
open project_name:
    uv run davinci-resolve-mcp open-project {{project_name}} --create

# Render a timeline
render timeline output:
    uv run davinci-resolve-mcp render {{output}} --timeline {{timeline}}

# Run a Resolve Python script
run-script script:
    uv run davinci-resolve-mcp run-script {{script}}

# ── Clean ─────────────────────────────────────────────────────────────────────

# Remove __pycache__ and .pyc files
clean-pyc:
    Get-ChildItem -Recurse -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Filter '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue

# Full clean (pycache + test cache + builds)
clean:
    just clean-pyc
    Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue

# ── Build ─────────────────────────────────────────────────────────────────────

# Build Python package
build:
    uv build

# Install locally (editable + dev)
dev:
    uv sync --all-extras
    uv pip install -e .

# ── Stats ─────────────────────────────────────────────────────────────────────

# Repo statistics (tools, files, coverage)
stats:
    uv run python tools/repo_stats.py

# Quick line count
count:
    Get-ChildItem -Recurse -Include '*.py' | Get-Content | Measure-Object -Line | Select-Object -ExpandProperty Lines
