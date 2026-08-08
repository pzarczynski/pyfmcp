# Usage

Install PyFMCP in the project environment, then start the server:

```bash
uv run pyfmcp
```

The `pyfmcp` command reads process configuration from command-line arguments and `PYFMCP_*` environment variables. By default it uses stdio transport, the current directory as the project root, and registers all available tools.

For HTTP transport, configure `transport=http`, then set `host` and `port` as needed. MCP clients should launch the command from the project they want to inspect, or pass an explicit root directory.
