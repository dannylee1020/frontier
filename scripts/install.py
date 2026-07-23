#!/usr/bin/env python3
"""Install the canonical Frontier skill for supported coding agents."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Iterable


AGENT_DESTINATIONS = {
    "claude": Path.home() / ".claude" / "skills" / "frontier",
    # OpenCode also discovers the shared Agent Skills directory. Keeping one
    # destination for Codex and OpenCode avoids duplicate skill definitions.
    "codex": Path.home() / ".agents" / "skills" / "frontier",
    "opencode": Path.home() / ".agents" / "skills" / "frontier",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def source_dir() -> Path:
    return project_root() / "skills" / "frontier"


def destinations(agents: Iterable[str]) -> list[tuple[str, Path]]:
    result: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for agent in agents:
        destination = AGENT_DESTINATIONS[agent].expanduser()
        if destination not in seen:
            seen.add(destination)
            result.append((agent, destination))
    return result


def install(agents: Iterable[str], *, force: bool = False, dry_run: bool = False) -> int:
    source = source_dir()
    if not source.is_dir():
        print(f"source skill not found: {source}", file=sys.stderr)
        return 1
    for agent, destination in destinations(agents):
        action = "would install" if dry_run else "installing"
        print(f"{action} {agent}: {source} -> {destination}")
        if dry_run:
            continue
        if destination.exists() or destination.is_symlink():
            if not force:
                print(f"destination exists; use --force: {destination}", file=sys.stderr)
                return 2
            if destination.is_dir() and not destination.is_symlink():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination)
    return 0


def uninstall(agents: Iterable[str], *, dry_run: bool = False) -> int:
    for agent, destination in destinations(agents):
        if not destination.exists() and not destination.is_symlink():
            print(f"not installed {agent}: {destination}")
            continue
        action = "would remove" if dry_run else "removing"
        print(f"{action} {agent}: {destination}")
        if dry_run:
            continue
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install or remove the Frontier agent skill.")
    parser.add_argument(
        "--agent",
        choices=["claude", "codex", "opencode", "all"],
        default="all",
        help="Target runtime (default: all).",
    )
    parser.add_argument("--uninstall", action="store_true", help="Remove installed copies.")
    parser.add_argument("--force", action="store_true", help="Replace existing copies when installing.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without changing files.")
    return parser


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 12):
        print("Frontier requires Python 3.12 or newer.", file=sys.stderr)
        return 2
    args = build_parser().parse_args(argv)
    agents = ["claude", "codex", "opencode"] if args.agent == "all" else [args.agent]
    if args.uninstall:
        return uninstall(agents, dry_run=args.dry_run)
    return install(agents, force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
