"""Query construction for the broad X social-momentum lane."""

from __future__ import annotations

import re


MAX_RECENT_QUERY_LENGTH = 512
_RETWEET_FILTER = re.compile(r"(?:^|\s)-is:retweet(?:\s|$)", re.IGNORECASE)


def build_x_query(query: str, *, max_length: int = MAX_RECENT_QUERY_LENGTH) -> str:
    """Build one bounded Recent Search query for one discovery branch.

    Branches remain independent so the artifact can show which semantic angle
    produced a post. The retweet exclusion reduces duplicate attention without
    removing original posts, replies, or quote posts.
    """

    cleaned = " ".join(str(query).split()).strip()
    if not cleaned:
        raise ValueError("X query cannot be empty")
    compiled = cleaned if _RETWEET_FILTER.search(cleaned) else f"{cleaned} -is:retweet"
    if len(compiled) > max_length:
        raise ValueError(
            f"X Recent Search query exceeds the {max_length}-character limit"
        )
    return compiled


def x_query_budget(queries: tuple[str, ...], total_limit: int, query: str) -> int:
    """Allocate a deterministic global post-read cap across branches."""

    if not queries or total_limit < 1:
        return 0
    try:
        index = queries.index(query)
    except ValueError:
        index = 0
    base, remainder = divmod(total_limit, len(queries))
    return base + (1 if index < remainder else 0)
