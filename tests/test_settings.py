"""Tests for runtime settings file loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyfmcp.config import Config
from pyfmcp.tools._settings import RuntimeSettings, load_settings


def test_missing_settings_returns_empty(tmp_path: Path) -> None:
    cfg = Config(root_dir=tmp_path)
    settings = load_settings(cfg)
    assert settings == RuntimeSettings()


def test_invalid_yaml_raises_with_settings_path(tmp_path: Path) -> None:
    cfg = Config(root_dir=tmp_path)
    (tmp_path / cfg.settings_file).write_text("tools: [unclosed\n")

    with pytest.raises(ValueError, match=r"pyfmcp.yml"):
        load_settings(cfg)
