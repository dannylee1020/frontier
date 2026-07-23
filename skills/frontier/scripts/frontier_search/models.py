"""Data models for the Frontier search pipeline.

The models deliberately use only the Python standard library so the installed
skill can run without a package installation step.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any


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
    artifact_limit: int = 20

    def to_dict(self) -> dict[str, Any]:
        return {
            "queries": list(self.queries),
            "since": self.since.isoformat(),
            "until": self.until.isoformat(),
            "candidate_limit": self.candidate_limit,
            "per_source_limit": self.per_source_limit,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "artifact_limit": self.artifact_limit,
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "query": self.query,
            "status": self.status,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "result_count": len(self.papers),
        }


@dataclass
class ArtifactRecord:
    """One provider's representation of a model or repository artifact."""

    source: str
    query: str
    source_rank: int
    artifact_type: str
    title: str
    description: str | None = None
    url: str | None = None
    identifier: str | None = None
    owner: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    language: str | None = None
    license: str | None = None
    tags: list[str] = field(default_factory=list)
    authority: str = "unknown"
    evidence_level: str = "metadata-only"
    source_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArtifactSearchResponse:
    source: str
    query: str
    status: str
    artifacts: list[ArtifactRecord] = field(default_factory=list)
    error: str | None = None
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "query": self.query,
            "status": self.status,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "result_count": len(self.artifacts),
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
    matched_queries: list[str] = field(default_factory=list)
    source_ranks: dict[str, list[int]] = field(default_factory=dict)
    source_scores: dict[str, list[float]] = field(default_factory=dict)
    source_identifiers: dict[str, list[str]] = field(default_factory=dict)
    evidence_level: str = "metadata-only"
    fusion_score: float = 0.0
    source_count: int = 0
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
            "matched_queries": list(self.matched_queries),
            "source_ranks": {key: list(value) for key, value in self.source_ranks.items()},
            "source_scores": {key: list(value) for key, value in self.source_scores.items()},
            "source_identifiers": {
                key: list(value) for key, value in self.source_identifiers.items()
            },
            "evidence_level": self.evidence_level,
            "fusion_score": round(self.fusion_score, 8),
            "source_count": self.source_count,
        }


@dataclass
class Artifact:
    """A normalized, possibly multi-query model or repository artifact."""

    artifact_type: str
    title: str
    description: str | None = None
    url: str | None = None
    identifier: str | None = None
    owner: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    language: str | None = None
    license: str | None = None
    tags: list[str] = field(default_factory=list)
    source: str = ""
    evidence_level: str = "metadata-only"
    matched_queries: list[str] = field(default_factory=list)
    source_ranks: dict[str, list[int]] = field(default_factory=dict)
    authority: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)
    fusion_score: float = 0.0
    source_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_type": self.artifact_type,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "identifier": self.identifier,
            "owner": self.owner,
            "published_at": self.published_at,
            "updated_at": self.updated_at,
            "language": self.language,
            "license": self.license,
            "tags": list(self.tags),
            "source": self.source,
            "matched_queries": list(self.matched_queries),
            "source_ranks": {key: list(value) for key, value in self.source_ranks.items()},
            "authority": self.authority,
            "evidence_level": self.evidence_level,
            "metadata": dict(self.metadata),
            "fusion_score": round(self.fusion_score, 8),
            "source_count": self.source_count,
        }


@dataclass
class SearchRun:
    request: SearchRequest
    executed_at: str
    responses: list[SearchResponse]
    papers: list[Paper]
    counts: dict[str, int]
    artifact_responses: list[ArtifactSearchResponse] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        statuses: dict[str, dict[str, Any]] = {}
        for response in [*self.responses, *self.artifact_responses]:
            current = statuses.setdefault(response.source, {"status": "ok", "errors": []})
            if response.status != "ok":
                current["status"] = "partial" if current["status"] == "ok" else current["status"]
                if response.error:
                    current["errors"].append(response.error)
            current.setdefault("queries", []).append(response.query)
            result_count = len(response.papers) if isinstance(response, SearchResponse) else len(response.artifacts)
            current.setdefault("result_counts", []).append(result_count)

        return {
            "request": self.request.to_dict(),
            "executed_at": self.executed_at,
            "source_status": statuses,
            "counts": dict(self.counts),
            "responses": [response.to_dict() for response in self.responses],
            "artifact_responses": [response.to_dict() for response in self.artifact_responses],
            "papers": [paper.to_dict() for paper in self.papers],
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
        }


def merge_unique(existing: list[str], new_values: list[str]) -> None:
    existing[:] = _unique(existing + new_values)
