"""Local clustering and momentum labeling for normalized X posts."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import XPost, XTrend, merge_unique
from .normalize import clean_text, normalize_title

_STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "been",
    "being",
    "but",
    "for",
    "from",
    "have",
    "into",
    "more",
    "not",
    "that",
    "the",
    "their",
    "this",
    "through",
    "with",
}
_URL_TRACKING = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src"}


def canonical_url(url: str) -> str:
    """Remove common tracking parameters while retaining the linked artifact."""

    try:
        parsed = urlsplit(url)
    except ValueError:
        return url
    query = [
        item for item in parse_qsl(parsed.query, keep_blank_values=True)
        if item[0].casefold() not in _URL_TRACKING
    ]
    return urlunsplit(
        (
            parsed.scheme.casefold(),
            parsed.netloc.casefold(),
            parsed.path.rstrip("/"),
            urlencode(query),
            "",
        )
    )


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]{3,}", normalize_title(text))
        if token not in _STOPWORDS
    }


def _attention(post: XPost) -> float:
    """Return an attention score, never a credibility score."""

    metrics = post.public_metrics
    impressions = metrics.get("impression_count", 0)
    likes = metrics.get("like_count", 0)
    reposts = metrics.get("retweet_count", 0)
    quotes = metrics.get("quote_count", 0)
    replies = metrics.get("reply_count", 0)
    bookmarks = metrics.get("bookmark_count", 0)
    raw = (
        math.log1p(max(impressions, 0))
        + 2.0 * math.log1p(max(likes, 0))
        + 2.0 * math.log1p(max(reposts, 0))
        + 2.0 * math.log1p(max(quotes, 0))
        + math.log1p(max(replies, 0))
        + math.log1p(max(bookmarks, 0))
    )
    # A recent post has had less time to accumulate attention. This adjusts
    # momentum for age without treating age or reach as evidence quality.
    from datetime import datetime, timezone

    try:
        created = datetime.fromisoformat((post.created_at or "").replace("Z", "+00:00"))
        age_hours = max(
            (datetime.now(timezone.utc) - created.astimezone(timezone.utc)).total_seconds()
            / 3600.0,
            1.0,
        )
    except ValueError:
        age_hours = 24.0
    return raw / math.sqrt(age_hours)


def deduplicate_posts(posts: list[XPost]) -> list[XPost]:
    """Collapse repeated IDs and edited versions without merging authors."""

    result: list[XPost] = []
    identity_index: dict[str, int] = {}
    for post in posts:
        keys = [post.post_id, *post.edit_history_ids]
        match = next((identity_index[key] for key in keys if key in identity_index), None)
        if match is None:
            result.append(post)
            match = len(result) - 1
        else:
            existing = result[match]
            merge_unique(existing.matched_queries, post.matched_queries)
            merge_unique(existing.linked_urls, post.linked_urls)
            merge_unique(existing.edit_history_ids, post.edit_history_ids)
            if len(post.text) > len(existing.text):
                existing.text = post.text
            if not existing.username and post.username:
                existing.username = post.username
            if not existing.author_name and post.author_name:
                existing.author_name = post.author_name
            if existing.author_class == "unknown" and post.author_class != "unknown":
                existing.author_class = post.author_class
            for key, value in post.public_metrics.items():
                existing.public_metrics[key] = max(existing.public_metrics.get(key, 0), value)
        for key in keys:
            identity_index[key] = match
    return result


def _related(post: XPost, group: list[XPost]) -> bool:
    post_urls = {canonical_url(url) for url in post.linked_urls}
    post_refs = {item.get("id") for item in post.referenced_posts}
    post_tokens = _tokens(post.text)
    for other in group:
        if post.conversation_id and post.conversation_id == other.conversation_id:
            return True
        if post_urls and post_urls & {canonical_url(url) for url in other.linked_urls}:
            return True
        if post_refs and post_refs & {
            item.get("id") for item in other.referenced_posts
        }:
            return True
        other_tokens = _tokens(other.text)
        overlap = post_tokens & other_tokens
        union = post_tokens | other_tokens
        if len(overlap) >= 2 and union and len(overlap) / len(union) >= 0.45:
            return True
    return False


def _trend_title(group: list[XPost]) -> str:
    for post in sorted(group, key=_attention, reverse=True):
        text = clean_text(post.text)
        if text:
            return text[:140] + ("…" if len(text) > 140 else "")
    return "Unlabeled X discussion"


def cluster_posts(posts: list[XPost], *, truncated: bool = False) -> list[XTrend]:
    """Cluster related attention signals without treating them as corroboration."""

    unique_posts = deduplicate_posts(posts)
    groups: list[list[XPost]] = []
    for post in unique_posts:
        for group in groups:
            if _related(post, group):
                group.append(post)
                break
        else:
            groups.append([post])

    scored: list[tuple[list[XPost], float]] = []
    for group in groups:
        score = max((_attention(post) for post in group), default=0.0)
        score += math.log1p(len({post.author_id or post.username for post in group}))
        score += math.log1p(len(group))
        scored.append((group, score))
    scored.sort(key=lambda item: (-item[1], _trend_title(item[0]).casefold()))

    scores = [score for _group, score in scored]
    median = scores[len(scores) // 2] if scores else 0.0
    trends: list[XTrend] = []
    for index, (group, score) in enumerate(scored):
        authors = {post.author_id or post.username or post.post_id for post in group}
        queries: list[str] = []
        artifacts: list[str] = []
        representative: list[str] = []
        for post in group:
            merge_unique(queries, post.matched_queries)
            for url in post.linked_urls:
                canonical = canonical_url(url)
                if canonical not in {canonical_url(item) for item in artifacts}:
                    artifacts.append(url)
        for post in sorted(group, key=_attention, reverse=True)[:3]:
            if post.url:
                representative.append(post.url)

        percentile = 1.0 if len(scores) == 1 else 1.0 - (index / max(len(scores) - 1, 1))
        if len(group) == 1 and score >= max(median * 2.0, 1.0):
            momentum_label = "high"
            trend_type = "viral-post"
        elif percentile >= 0.75 and (len(group) >= 3 or len(authors) >= 3):
            momentum_label = "high"
            trend_type = "emerging-discussion"
        elif len(group) >= 2 or len(authors) >= 2:
            momentum_label = "medium" if percentile >= 0.4 else "low"
            trend_type = "discussion"
        else:
            momentum_label = "low"
            trend_type = "single-post"

        limitations = [
            "Attention metrics measure visibility, not credibility or technical validity."
        ]
        if len(authors) <= 1:
            limitations.append("Attention is concentrated in one author or origin.")
        if not artifacts:
            limitations.append("No canonical artifact link was found in the retrieved posts.")
        if truncated:
            limitations.append("The X result set was capped; this is not exhaustive coverage.")
        trends.append(
            XTrend(
                title=_trend_title(group),
                matched_queries=queries,
                first_seen=min(
                    (post.created_at for post in group if post.created_at),
                    default=None,
                ),
                last_seen=max(
                    (post.created_at for post in group if post.created_at),
                    default=None,
                ),
                post_count=len(group),
                unique_author_count=len(authors),
                momentum_score=score,
                momentum_label=momentum_label,
                trend_type=trend_type,
                evidence_state="artifact-linked" if artifacts else "x-only",
                representative_posts=representative,
                linked_artifacts=artifacts,
                limitations=limitations,
            )
        )
    return trends
