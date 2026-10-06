set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# --- Dashboard ---

# Open the interactive recipe dashboard in the browser
default:
    @just --list


# Synchronize deps, pre-commit hooks, and web frontend
bootstrap:
    uv sync --extra dev --group dev
    uv run pre-commit install
    Set-Location web_sota; npm ci; if ($LASTEXITCODE -ne 0) { npm install }
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green
# --- Quality ---

# Ruff lint (Python) + Biome CI check (webapp)
lint:
    Set-Location '{{justfile_directory()}}'; uv run ruff check .; Set-Location '{{justfile_directory()}}\web_sota'; npx @biomejs/biome ci .

# Ruff fix + format (Python) + Biome format (webapp)
fix:
    Set-Location '{{justfile_directory()}}'; uv run ruff check . --fix --unsafe-fixes; uv run ruff format .; Set-Location '{{justfile_directory()}}\web_sota'; npx @biomejs/biome check --write .

# Quick ruff check only (fast feedback loop)
ruff-check:
    uv run ruff check .

# --- Testing ---

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

# --- Security ---

# Bandit security audit
check-sec:
    uv run bandit -r src/

# Safety dependency audit
audit-deps:
    uv run pip-audit

# --- Development ---

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

# --- Run Modes ---

# --- Run MCP server  stdio  for Claude Desktop  Cursor ---
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

# --- CLI Direct ---

# Open a project (create if needed)
open project_name:
    uv run davinci-resolve-mcp open-project {{project_name}} --create

# Render a timeline
render timeline output:
    uv run davinci-resolve-mcp render {{output}} --timeline {{timeline}}

# Run a Resolve Python script
run-script script:
    uv run davinci-resolve-mcp run-script {{script}}

# --- Clean ---

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

# --- Build ---

# Build Python package
build:
    uv build

# Install locally (editable + dev)
dev:
    uv sync --all-extras
    uv pip install -e .

# --- Stats ---

# Repo statistics (tools, files, coverage)
stats:
    uv run python tools/repo_stats.py

# Quick line count
count:
    Get-ChildItem -Recurse -Include '*.py' | Get-Content | Measure-Object -Line | Select-Object -ExpandProperty Lines


# Format Python (ruff format) — pairs with lint
fmt:
    uv run ruff format .

# Serve the HTTP API backend (port 10843, fleet engine contract: api_app)
serve:
    uv run uvicorn davinci_resolve_mcp.server:api_app --host 127.0.0.1 --port 10843

# Local five-gate CI: ruff + format-check + pytest + tsc + biome
ci:
    uv run ruff check .
    uv run ruff format . --check
    uv run pytest tests/unit/ -q --timeout=30
    npx tsc --noEmit
    npx @biomejs/biome ci web_sota/src

# MCPB pack with fresh stage (wipe+recopy src/ -> mcpb/src/ before pack)
mcpb-pack:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File '{{justfile_directory()}}\scripts\mcpb-pack-inline.ps1'

# Build the Tauri native wrapper (requires Rust + Node)
build-native:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File '{{justfile_directory()}}\native\build.ps1'

# CUA NSIS smoke test (post-install UI walk)
cua-nsis-test:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File '{{justfile_directory()}}\scripts\just\cua-nsis-test.ps1'

# CUA webapp smoke test (pre-Tauri browser walk)
cua-webapp-test:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File '{{justfile_directory()}}\scripts\just\cua-webapp-test.ps1'

# Bootstrap: install dev deps + pre-commit hook
