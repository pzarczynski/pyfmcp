# Configuration and settings

PyFMCP has two configuration layers:

1. **Process configuration** controls how the MCP server starts. It is loaded once from command-line arguments and `PYFMCP_*` environment variables.
2. **Runtime tool settings** control individual checks. They are loaded from YAML each time a tool is invoked, so changes take effect without restarting the server.

## Process configuration

| Setting | Default | Description |
| --- | --- | --- |
| `tools` | all tools | Tools to register: `pytest`, `ruff`, and `basedpyright`. |
| `transport` | `stdio` | MCP transport: `stdio` or `http`. |
| `host` | `localhost` | HTTP bind host; used with `transport=http`. |
| `port` | `4444` | HTTP bind port; used with `transport=http`. |
| `root_dir` | current directory | Project directory checked by tools. |
| `settings_file` | `pyfmcp.yml` | YAML settings filename, resolved relative to `root_dir`. |

For environment variables, prefix the setting name with `PYFMCP_`, for example `PYFMCP_TRANSPORT=http` or `PYFMCP_ROOT_DIR=/work/project`. CLI options take precedence over environment values when both are supplied.

## Runtime tool settings

Create the configured settings file in the project root. The top-level keys are tool names; each value is validated when that tool is called:

```yaml
tools:
  pytest:
    test_args: [-q]
    timeout: 120
  ruff_lint:
    max_diagnostics: 100
    diagnostic_length: 200
    timeout: 60
  basedpyright:
    max_diagnostics: 100
    diagnostic_length: 200
    timeout: 60
```

Available settings are:

- `timeout`: optional command timeout in seconds, shared by all tools.
- `pytest.test_args`: extra arguments appended to pytest invocations.
- `ruff_lint.max_diagnostics`: optional maximum number of diagnostics returned.
- `ruff_lint.diagnostic_length`: optional maximum length of each diagnostic message.
- `basedpyright.max_diagnostics`: optional maximum number of diagnostics returned.
- `basedpyright.diagnostic_length`: optional maximum length of each diagnostic message.

A missing settings file is valid and means that every tool uses its defaults. An invalid YAML document or an invalid setting raises an explicit configuration error; it is not silently ignored. Settings are passed only to registered tools, and the file is read once per tool invocation.

## Selecting tools

By default, all three tools are registered. Restrict registration through process configuration, for example with a CLI value or `PYFMCP_TOOLS`:

```text
pytest,ruff_lint
```

Unknown tool names are rejected during startup.
