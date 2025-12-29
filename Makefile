# DaVinci Resolve MCP Server - Development Makefile
# Compatible with Windows (using PowerShell) and Unix-like systems

.PHONY: help install install-dev test test-unit test-integration test-coverage lint format type-check build clean check all

# Default target
help:
	@echo "DaVinci Resolve MCP Server - Development Commands"
	@echo "================================================="
	@echo "install-dev    - Install development dependencies"
	@echo "test           - Run all tests"
	@echo "test-unit      - Run unit tests only"
	@echo "test-integration - Run integration tests only"
	@echo "test-coverage  - Run tests with coverage report"
	@echo "lint           - Run linting checks"
	@echo "format         - Format code with ruff"
	@echo "type-check     - Run type checking with mypy"
	@echo "build          - Build Python package"
	@echo "clean          - Clean build artifacts"
	@echo "check          - Run all checks (lint, type-check)"
	@echo "all            - Run all checks and tests"

# Install development dependencies
install-dev:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

# Run all tests
test:
	pytest tests/ -v

# Run unit tests only
test-unit:
	pytest tests/unit/ -v -m "not integration and not slow"

# Run integration tests only
test-integration:
	pytest tests/integration/ -v -m integration

# Run tests with coverage
test-coverage:
	pytest tests/ --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml

# Run linting checks
lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

# Format code
format:
	ruff format src/ tests/

# Run type checking
type-check:
	python -m mypy src/ --ignore-missing-imports

# Build Python package
build:
	python -m build

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run all checks (lint, format check, type check)
check: lint type-check

# Run all checks and tests
all: lint type-check test-coverage build

# Windows-specific targets (using PowerShell)
ifeq ($(OS),Windows_NT)
clean:
	powershell -Command "Remove-Item -Recurse -Force build, dist, *.egg-info, htmlcov, .coverage, .pytest_cache, .mypy_cache -ErrorAction SilentlyContinue"
	powershell -Command "Get-ChildItem -Recurse -Directory -Name __pycache__ | Remove-Item -Recurse -Force"
	powershell -Command "Get-ChildItem -Recurse -Filter *.pyc | Remove-Item -Force"
endif
