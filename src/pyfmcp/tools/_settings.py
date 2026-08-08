"""Startup-loaded project settings."""

import msgspec

from pyfmcp.config import Config


class RuntimeSettings(msgspec.Struct, frozen=True):
    """Validated per-tool settings from the runtime YAML file."""

    tools: dict[str, object] = msgspec.field(default_factory=dict)


def load_settings(cfg: Config) -> RuntimeSettings:
    """Load and validate the current runtime settings file."""
    path = cfg.root_dir / cfg.settings_file
    if not path.is_file():
        return RuntimeSettings()
    try:
        return msgspec.yaml.decode(path.read_bytes(), type=RuntimeSettings)
    except (msgspec.DecodeError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid runtime configuration {path}: {exc}") from exc
