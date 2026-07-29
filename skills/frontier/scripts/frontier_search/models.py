"""Data models for the Frontier research search pipeline.

The models deliberately use only the Python standard library so the installed
skill can run without a package installation step.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any


SCHOLARLY_SOURCES = frozenset({"openalex", "arxiv", "semantic_scholar"})
MOMENTUM_SOURCES = frozenset({"huggingface_papers"})
SOCIAL_SOURCES = frozenset({"x_recent"})


def source_role(source: str) -> str:
    """Return the semantic role of a paper source."""

    return "momentum" if source in MOMENTUM_SOURCES else "scholarly"


def utc_now() -> str:
    """Return a stable, timezone-aware timestamp for run artifacts."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _unique(values: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


@dataclass(frozen=True)
class SearchRequest:
    queries: tuple[str, ...]
    since: date
    until: date
    candidate_limit: int = 30
    per_source_limit: int = 20
    timeout_seconds: float = 20.0
    max_retries: int = 2
    x_enabled: bool = False
    x_days: int = 7
    x_candidate_limit: int = 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "queries": list(self.queries),
            "since": self.since.isoformat(),
            "until": self.until.isoformat(),
            "candidate_limit": self.candidate_limit,
            "per_source_limit": self.per_source_limit,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "x_enabled": self.x_enabled,
            "x_days": self.x_days,
            "x_candidate_limit": self.x_candidate_limit,
        }


@dataclass
class SourceRecord:
    """One provider's representation of a paper."""

    source: str
    query: str
    source_rank: int
    title: str
    authors: list[str] = field(default_factory=list)
    abstract: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    semantic_scholar_id: str | None = None
    venue: str | None = None
    publication_status: str = "unknown"
    urls: list[str] = field(default_factory=list)
    source_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResponse:
    source: str
    query: str
    status: str
    papers: list[SourceRecord] = field(default_factory=list)
    error: str | None = None
    duration_ms: int = 0
    role: str = "scholarly"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "role": self.role,
            "query": self.query,
            "status": self.status,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "result_count": len(self.papers),
        }


@dataclass
class Paper:
    """A normalized, possibly multi-provider paper record."""

    title: str
    authors: list[str] = field(default_factory=list)
    abstract: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    semantic_scholar_id: str | None = None
    venue: str | None = None
    publication_status: str = "unknown"
    urls: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    scholarly_sources: list[str] = field(default_factory=list)
    momentum_sources: list[str] = field(default_factory=list)
    matched_queries: list[str] = field(default_factory=list)
    source_ranks: dict[str, list[int]] = field(default_factory=dict)
    momentum_ranks: dict[str, list[int]] = field(default_factory=dict)
    source_scores: dict[str, list[float]] = field(default_factory=dict)
    source_identifiers: dict[str, list[str]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    evidence_level: str = "metadata-only"
    fusion_score: float = 0.0
    momentum_score: float = 0.0
    source_count: int = 0
    scholarly_source_count: int = 0
    title_key: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "authors": list(self.authors),
            "abstract": self.abstract,
            "published_at": self.published_at,
            "updated_at": self.updated_at,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "semantic_scholar_id": self.semantic_scholar_id,
            "venue": self.venue,
            "publication_status": self.publication_status,
            "urls": list(self.urls),
            "sources": list(self.sources),
            "scholarly_sources": list(self.scholarly_sources),
            "momentum_sources": list(self.momentum_sources),
            "matched_queries": list(self.matched_queries),
            "source_ranks": {key: list(value) for key, value in self.source_ranks.items()},
            "momentum_ranks": {
                key: list(value) for key, value in self.momentum_ranks.items()
            },
            "source_scores": {key: list(value) for key, value in self.source_scores.items()},
            "source_identifiers": {
                key: list(value) for key, value in self.source_identifiers.items()
            },
            "metadata": dict(self.metadata),
            "evidence_level": self.evidence_level,
            "fusion_score": round(self.fusion_score, 8),
            "momentum_score": round(self.momentum_score, 8),
            "source_count": self.source_count,
            "scholarly_source_count": self.scholarly_source_count,
        }


@dataclass
class XPost:
    """A normalized X post kept separate from scholarly paper records."""

    post_id: str
    text: str
    author_id: str | None = None
    username: str | None = None
    author_name: str | None = None
    organization: str = "unknown"
    author_class: str = "unknown"
    created_at: str | None = None
    url: str | None = None
    conversation_id: str | None = None
    referenced_posts: list[dict[str, str]] = field(default_factory=list)
    linked_urls: list[str] = field(default_factory=list)
    public_metrics: dict[str, int] = field(default_factory=dict)
    matched_queries: list[str] = field(default_factory=list)
    edit_history_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "post_id": self.post_id,
            "text": self.text,
            "author_id": self.author_id,
            "username": self.username,
            "author_name": self.author_name,
            "organization": self.organization,
            "author_class": self.author_class,
            "created_at": self.created_at,
            "url": self.url,
            "conversation_id": self.conversation_id,
            "referenced_posts": [dict(item) for item in self.referenced_posts],
            "linked_urls": list(self.linked_urls),
            "public_metrics": dict(self.public_metrics),
            "matched_queries": list(self.matched_queries),
            "edit_history_ids": list(self.edit_history_ids),
        }


@dataclass
class XSearchResponse:
    """One X API query response, including the effective recent window."""

    source: str
    query: str
    status: str
    posts: list[XPost] = field(default_factory=list)
    effective_since: str | None = None
    effective_until: str | None = None
    error: str | None = None
    truncated: bool = False
    duration_ms: int = 0
    api_query: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "role": "social_momentum",
            "query": self.query,
            "api_query": self.api_query,
            "status": self.status,
            "effective_since": self.effective_since,
            "effective_until": self.effective_until,
            "error": self.error,
            "truncated": self.truncated,
            "duration_ms": self.duration_ms,
            "result_count": len(self.posts),
        }


@dataclass
class XTrend:
    """A locally clustered social-attention signal, not a truth claim."""

    title: str
    matched_queries: list[str] = field(default_factory=list)
    first_seen: str | None = None
    last_seen: str | None = None
    post_count: int = 0
    unique_author_count: int = 0
    momentum_score: float = 0.0
    momentum_label: str = "low"
    trend_type: str = "single-post"
    evidence_state: str = "unreviewed"
    representative_posts: list[str] = field(default_factory=list)
    linked_artifacts: list[str] = field(default_factory=list)
    supporting_views: list[str] = field(default_factory=list)
    counter_views: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "matched_queries": list(self.matched_queries),
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "post_count": self.post_count,
            "unique_author_count": self.unique_author_count,
            "momentum_score": round(self.momentum_score, 8),
            "momentum_label": self.momentum_label,
            "trend_type": self.trend_type,
            "evidence_state": self.evidence_state,
            "representative_posts": list(self.representative_posts),
            "linked_artifacts": list(self.linked_artifacts),
            "supporting_views": list(self.supporting_views),
            "counter_views": list(self.counter_views),
            "limitations": list(self.limitations),
        }


@dataclass
class SearchRun:
    request: SearchRequest
    executed_at: str
    responses: list[SearchResponse]
    papers: list[Paper]
    counts: dict[str, int]
    momentum_responses: list[SearchResponse] = field(default_factory=list)
    x_responses: list[XSearchResponse] = field(default_factory=list)
    x_posts: list[XPost] = field(default_factory=list)
    x_trends: list[XTrend] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        statuses: dict[str, dict[str, Any]] = {}
        for response in [*self.responses, *self.momentum_responses]:
            current = statuses.setdefault(
                response.source,
                {"role": response.role, "status": "ok", "errors": []},
            )
            current.setdefault("response_statuses", []).append(response.status)
            if response.status != "ok":
                if current["status"] == "ok":
                    current["status"] = (
                        "rate-limited"
                        if response.status == "rate-limited"
                        else "partial"
                    )
                elif current["status"] == "rate-limited" and response.status != "rate-limited":
                    current["status"] = "partial"
                if response.error:
                    current["errors"].append(response.error)
            elif current["status"] == "rate-limited":
                current["status"] = "partial"
            current.setdefault("queries", []).append(response.query)
            current.setdefault("result_counts", []).append(len(response.papers))

        # X is deliberately summarized outside the paper-provider loop. Its
        # records are social-attention evidence, not paper evidence, and its
        # statuses need to preserve all-unavailable/all-error states.
        if self.x_responses:
            x_statuses: dict[str, list[str]] = {}
            for response in self.x_responses:
                current = statuses.setdefault(
                    response.source,
                    {"role": "social_momentum", "status": "ok", "errors": []},
                )
                x_statuses.setdefault(response.source, []).append(response.status)
                current.setdefault("response_statuses", []).append(response.status)
                current.setdefault("queries", []).append(response.query)
                current.setdefault("result_counts", []).append(len(response.posts))
                current.setdefault("effective_windows", []).append(
                    {
                        "since": response.effective_since,
                        "until": response.effective_until,
                    }
                )
                current["truncated"] = bool(current.get("truncated")) or response.truncated
                if response.error:
                    current["errors"].append(response.error)

            for source, source_statuses in x_statuses.items():
                current = statuses[source]
                if all(status == "ok" for status in source_statuses):
                    current["status"] = "ok"
                elif all(status == "unavailable" for status in source_statuses):
                    current["status"] = "unavailable"
                elif all(status == "rate-limited" for status in source_statuses):
                    current["status"] = "rate-limited"
                elif all(status == "error" for status in source_statuses):
                    current["status"] = "error"
                else:
                    current["status"] = "partial"

        return {
            "request": self.request.to_dict(),
            "executed_at": self.executed_at,
            "source_status": statuses,
            "counts": dict(self.counts),
            "responses": [response.to_dict() for response in self.responses],
            "momentum_responses": [
                response.to_dict() for response in self.momentum_responses
            ],
            "x_responses": [response.to_dict() for response in self.x_responses],
            "papers": [paper.to_dict() for paper in self.papers],
            "x_posts": [post.to_dict() for post in self.x_posts],
            "x_trends": [trend.to_dict() for trend in self.x_trends],
        }


def merge_unique(existing: list[str], new_values: list[str]) -> None:
    existing[:] = _unique(existing + new_values)
