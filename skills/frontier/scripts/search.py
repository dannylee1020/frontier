#!/usr/bin/env python3
"""Executable wrapper for the Frontier search utility."""

from __future__ import annotations

import sys
from pathlib import Path

if sys.version_info < (3, 12):
    raise SystemExit("Frontier requires Python 3.12 or newer.")

# Make the sibling package importable when this file is invoked directly.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from frontier_search.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
