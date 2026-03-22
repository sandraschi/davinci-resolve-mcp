# Development

## Setup

```text
git clone https://github.com/sandraschi/davinci-resolve-mcp
cd davinci-resolve-mcp
uv sync --extra dev
```

Activate the venv if you use one, then:

```text
uv run pytest tests/ -v
uv run ruff check src tests
uv run ruff format src tests
```

Pre-commit (optional):

```text
uv run pre-commit install
```

## Layout

See [ARCHITECTURE.md](ARCHITECTURE.md#repository-layout-abbreviated).

## Tests

```text
uv run pytest tests/ -v --cov=src/davinci_resolve_mcp
uv run pytest tests/unit/
uv run pytest tests/integration/
```

## Builds

```text
python -m build
python build_mcpb.py
python -m scripts.build_zed
```

## Contributing

1. Fork and branch from `main` / `master` as upstream uses.  
2. Install with `uv sync --extra dev`.  
3. Run tests and Ruff before pushing.  
4. Open a PR with a short description of behavior and risk.

If the repo adds a `CONTRIBUTING.md`, follow that file; otherwise use the above.

## Release (maintainers)

1. Bump version in `pyproject.toml` and `CHANGELOG.md` (if present).  
2. Tag.  
3. Let CI publish PyPI / MCPB / GitHub release per pipeline configuration.
