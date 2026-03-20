# davinci-resolve-mcp — just recipes
# Run with: just [recipe]

default:
    uv run davinci-resolve-mcp

# Install/sync dependencies (uv)
install sync:
    uv sync

# Install with dev dependencies
install-dev:
    uv sync --all-extras

# Run MCP server (explicit)
run:
    uv run davinci-resolve-mcp

# Lint and format (Ruff)
lint:
    uv run ruff check .
format:
    uv run ruff format .

# Run tests
test:
    uv run pytest
