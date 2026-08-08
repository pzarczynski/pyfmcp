# PyFMCP

A focused [Model Context Protocol](https://modelcontextprotocol.io/) server for running Python project checks through pytest, Ruff, and basedpyright.

## What it provides

- One MCP server with configurable project-root handling.
- Structured results instead of raw subprocess output.
- Per-invocation loading of tool settings from `pyfmcp.yml`.
- Strict typing and small, independently testable tool adapters.

See [Usage](usage.md) to run the server and [Configuration](configuration.md) to select tools and configure their commands.
