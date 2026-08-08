from pathlib import Path

from pyfmcp.config import load
from pyfmcp.server import create_mcp


def main() -> None:
    """Load configuration and run the configured MCP transport."""

    config = load()
    project_root = Path.cwd()
    mcp = create_mcp(project_root, config)
    mcp.run(config.transport)


if __name__ == "__main__":
    main()
