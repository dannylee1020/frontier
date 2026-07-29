"""Command-line interface for the Frontier search utility."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Sequence

from .config import load_frontier_env, x_enabled_by_config
from .models import SearchRequest
from .search import run_search
from .sources.x_recent import XRecentAdapter


VERSION = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="frontier-search",
        description=(
            "Search scholarly papers, Hugging Face momentum, and optionally "
            "broad X social momentum; emit normalized JSON."
        ),
    )
    parser.add_argument(
        "--query",
        action="append",
        required=True,
        help="Search query; repeat up to three times for discovery branches.",
    )
    parser.add_argument(
        "--since",
        type=date.fromisoformat,
        help="Inclusive publication date (YYYY-MM-DD); defaults to 90 days ago.",
    )
    parser.add_argument(
        "--until",
        type=date.fromisoformat,
        help="Inclusive publication date (YYYY-MM-DD); defaults to today.",
    )
    parser.add_argument(
        "--candidate-limit",
        type=int,
        default=30,
        help="Maximum merged candidates to return (default: 30).",
    )
    parser.add_argument(
        "--per-source-limit",
        type=int,
        default=20,
        help="Maximum results per provider and query (default: 20).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout in seconds (default: 20).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Retries for transient provider errors (default: 2).",
    )
    x_group = parser.add_mutually_exclusive_group()
    x_group.add_argument(
        "--x",
        action="store_true",
        help="Force-enable the broad X Recent Search momentum lane.",
    )
    x_group.add_argument(
        "--no-x",
        action="store_true",
        help="Disable X even when an X token is configured.",
    )
    parser.add_argument(
        "--x-days",
        type=int,
        default=7,
        help="X search window in days, from 1 through 7 (default: 7).",
    )
    parser.add_argument(
        "--x-candidate-limit",
        type=int,
        default=100,
        help="Global maximum X posts fetched across query branches (default: 100).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSON to this path instead of stdout.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # Load user-local provider credentials inside Frontier. Do not source the
    # file in the invoking shell: the parent agent must not inherit secrets.
    load_frontier_env()
    until = args.until or date.today()
    since = args.since or until - timedelta(days=90)
    if len(args.query) > 3:
        parser.error("--query may be supplied at most three times")
    if args.candidate_limit < 1 or args.per_source_limit < 1:
        parser.error("limits must be positive")
    if args.timeout <= 0 or args.max_retries < 0:
        parser.error("timeout must be positive and max-retries cannot be negative")
    if not 1 <= args.x_days <= 7:
        parser.error("--x-days must be between 1 and 7")
    if args.x_candidate_limit < 1:
        parser.error("--x-candidate-limit must be positive")
    x_configured = XRecentAdapter.is_configured()
    x_enabled = (
        not args.no_x
        and (args.x or (x_configured and x_enabled_by_config()))
    )
    if x_enabled:
        if args.x_candidate_limit < 10 * len(args.query):
            parser.error(
                "--x-candidate-limit must allocate at least 10 posts per query branch"
            )
        if not x_configured:
            parser.error("X_BEARER_TOKEN is required when X search is enabled")

    request = SearchRequest(
        queries=tuple(args.query),
        since=since,
        until=until,
        candidate_limit=args.candidate_limit,
        per_source_limit=args.per_source_limit,
        timeout_seconds=args.timeout,
        max_retries=args.max_retries,
        x_enabled=x_enabled,
        x_days=args.x_days,
        x_candidate_limit=args.x_candidate_limit,
    )
    try:
        run = run_search(request)
    except ValueError as error:
        parser.error(str(error))
    except KeyboardInterrupt:
        print("frontier search interrupted", file=sys.stderr)
        return 130

    rendered = json.dumps(run.to_dict(), indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0
