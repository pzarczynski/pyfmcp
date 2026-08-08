"""Configuration that is read when the server starts."""

from pathlib import Path
from typing import Literal

from structconfig import Struct, load_config


class Config(Struct):
    """Process-level settings used to start the MCP server."""

    tools: tuple[str, ...] | None = None
    transport: Literal["http", "stdio"] = "stdio"
    host: str = "localhost"
    port: int = 4444
    root_dir: Path = Path.cwd()
    settings_file: str = "pyfmcp.yml"


def load() -> Config:
    """Load process configuration from CLI arguments and the environment."""

    return load_config(Config, cli=True, env_prefix="PYFMCP")
