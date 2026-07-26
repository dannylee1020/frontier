"""Command-line interface for the Frontier search utility."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Sequence

from .models import SearchRequest
from .search import run_search


VERSION = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="frontier-search",
        description=(
            "Search scholarly papers and Hugging Face trending papers "
            "and emit normalized JSON."
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
    until = args.until or date.today()
    since = args.since or until - timedelta(days=90)
    if len(args.query) > 3:
        parser.error("--query may be supplied at most three times")
    if args.candidate_limit < 1 or args.per_source_limit < 1:
        parser.error("limits must be positive")
    if args.timeout <= 0 or args.max_retries < 0:
        parser.error("timeout must be positive and max-retries cannot be negative")

    request = SearchRequest(
        queries=tuple(args.query),
        since=since,
        until=until,
        candidate_limit=args.candidate_limit,
        per_source_limit=args.per_source_limit,
        timeout_seconds=args.timeout,
        max_retries=args.max_retries,
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
