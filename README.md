# pyfmcp

A focused [Model Context Protocol](https://modelcontextprotocol.io/) server for
running Python project checks through pytest, Ruff, and basedpyright.

## Requirements

- Python 3.12+
- An MCP-compatible client
- `uv` (recommended) or another Python package installer

## Install and run

Run it from the project you want to inspect:

```bash
uv run pyfmcp
```

The default transport is stdio. For HTTP, configure `transport=http` and set
`host` and `port` as needed. Process settings can be supplied as CLI options or
with `PYFMCP_*` environment variables. The current directory is the default
project root; use `root_dir` to select another project.

## Settings

Create `pyfmcp.yml` in the project root to configure checks. It is re-read for
each tool invocation:

```yaml
tools:
  pytest:
    test_args: [-q]
  ruff_lint:
    max_diagnostics: 100
  basedpyright:
    max_diagnostics: 100
```

Missing settings files use tool defaults. Invalid YAML or values produce a
configuration error. See the [configuration guide](docs/configuration.md) for
all process and tool settings.

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
