# PyFMCP

[![CI](https://github.com/pzarczynski/pyfmcp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/pzarczynski/pyfmcp/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/pyfmcp)](https://pypi.org/project/pyfmcp/)
[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://pzarczynski.github.io/PyFMCP/)

An easy-to-use, configurable, Python-focused [Model Context Protocol](https://modelcontextprotocol.io/) providing tools for type-checking, testing and linting your code.

## Requirements

- Python 3.12+
- An MCP-compatible client
- `uv` (recommended) or another Python package installer

## Usage

Run it from the project you want to inspect:

```bash
uv run pyfmcp
```

## Development

```bash
uv sync --all-groups
uv run pytest
uv run ruff check .
uv run basedpyright
```

Build the documentation with `uv run mkdocs serve`.

Contributions are welcome. Please open an issue or pull request with a focused
change, tests where appropriate, and documentation for user-visible behavior.

## License

[MIT](LICENSE)
