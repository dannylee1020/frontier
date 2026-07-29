"""Private Frontier dotenv loading for CLI-startup provider configuration."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


SUPPORTED_ENV_KEYS = frozenset(
    {
        "X_BEARER_TOKEN",
        "SEMANTIC_SCHOLAR_API_KEY",
        "OPENALEX_EMAIL",
        "FRONTIER_USER_AGENT",
        "FRONTIER_X_ENABLED",
    }
)
_ASSIGNMENT = re.compile(
    r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$"
)
_SHELL_SYNTAX = ("$(`", "$(", "${", "`")


def frontier_home() -> Path:
    """Return the user-local Frontier home without reading its contents."""

    override = os.environ.get("FRONTIER_HOME", "").strip()
    return Path(override).expanduser() if override else Path.home() / ".frontier"


def env_path() -> Path:
    return frontier_home() / ".env"


def _warn(message: str) -> None:
    sys.stderr.write(f"[frontier] WARNING: {message}\n")
    sys.stderr.flush()


def _check_permissions(path: Path) -> None:
    try:
        mode = path.stat().st_mode
        if mode & 0o077:
            _warn(f"{path} is accessible by group or other users; run: chmod 600 {path}")
        parent_mode = path.parent.stat().st_mode
        if parent_mode & 0o077:
            _warn(
                f"{path.parent} is accessible by group or other users; "
                f"run: chmod 700 {path.parent}"
            )
    except OSError:
        # The subsequent read produces the actionable path-only warning.
        return


def _strip_value(raw_value: str) -> str | None:
    value = raw_value.strip()
    if not value:
        return None
    if any(marker in value for marker in _SHELL_SYNTAX):
        return None
    if value[0] in {'"', "'"}:
        if len(value) < 2 or value[-1] != value[0]:
            return None
        value = value[1:-1]
    return value or None


def _parse(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _ASSIGNMENT.match(line)
        if not match:
            _warn(f"ignored invalid configuration syntax at line {line_number}")
            continue
        key, raw_value = match.groups()
        if key not in SUPPORTED_ENV_KEYS:
            continue
        value = _strip_value(raw_value)
        if value is None:
            _warn(f"ignored invalid value for {key} at line {line_number}")
            continue
        values[key] = value
    return values


def x_enabled_by_config() -> bool:
    """Return whether configured X retrieval is allowed by default."""

    value = os.environ.get("FRONTIER_X_ENABLED", "").strip().casefold()
    return value not in {"0", "false", "no", "off"}


def load_frontier_env() -> tuple[str, ...]:
    """Load private dotenv values into this process without shell execution.

    Existing process environment values win. The returned tuple contains only
    loaded key names, never secret values, and is intended for tests/diagnostics.
    """

    path = env_path()
    if not path.exists():
        return ()
    _check_permissions(path)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        _warn(f"could not read configuration file {path}")
        return ()

    loaded: list[str] = []
    for key, value in _parse(text).items():
        if key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return tuple(loaded)
