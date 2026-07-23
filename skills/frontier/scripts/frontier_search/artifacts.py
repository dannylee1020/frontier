"""Deduplication and ranking for model and repository artifacts."""

from __future__ import annotations

from typing import Iterable
from urllib.parse import urlsplit, urlunsplit

from .models import Artifact, ArtifactRecord, merge_unique

_AUTHORITY_ORDER = {
    "unknown": 0,
    "community": 10,
    "verified-owner": 20,
    "primary-official": 30,
}
_EVIDENCE_ORDER = {
    "metadata-only": 0,
    "card-or-readme": 10,
    "full-text": 20,
}
_RRF_K = 60


def _canonical_url(url: str | None) -> str:
    if not url:
        return ""
    parts = urlsplit(url.strip())
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.casefold(), parts.netloc.casefold(), path, "", ""))


def _key(record: ArtifactRecord | Artifact) -> str:
    if record.identifier:
        return f"{record.source}:{record.artifact_type}:{record.identifier.casefold()}"
    return f"{record.source}:{record.artifact_type}:{_canonical_url(record.url)}"


def _date_part(value: str | None) -> str | None:
    return value[:10] if value else None


def _record_to_artifact(record: ArtifactRecord) -> Artifact:
    return Artifact(
        artifact_type=record.artifact_type,
        title=record.title,
        description=record.description,
        url=record.url,
        identifier=record.identifier,
        owner=record.owner,
        published_at=_date_part(record.published_at),
        updated_at=_date_part(record.updated_at),
        language=record.language,
        license=record.license,
        tags=list(record.tags),
        source=record.source,
        matched_queries=[record.query],
        source_ranks={record.source: [record.source_rank]},
        authority=record.authority,
        evidence_level=record.evidence_level,
        metadata=dict(record.metadata),
        source_count=1,
    )


def _merge(artifact: Artifact, record: ArtifactRecord) -> None:
    if len(record.title) > len(artifact.title):
        artifact.title = record.title
    if record.description and (
        not artifact.description or len(record.description) > len(artifact.description)
    ):
        artifact.description = record.description
    artifact.url = artifact.url or record.url
    artifact.identifier = artifact.identifier or record.identifier
    artifact.owner = artifact.owner or record.owner
    artifact.published_at = min(
        value for value in (artifact.published_at, _date_part(record.published_at)) if value
    ) if artifact.published_at or record.published_at else None
    artifact.updated_at = max(
        value for value in (artifact.updated_at, _date_part(record.updated_at)) if value
    ) if artifact.updated_at or record.updated_at else None
    artifact.language = artifact.language or record.language
    artifact.license = artifact.license or record.license
    merge_unique(artifact.tags, record.tags)
    merge_unique(artifact.matched_queries, [record.query])
    artifact.source_ranks.setdefault(record.source, []).append(record.source_rank)
    artifact.source_ranks[record.source] = sorted(set(artifact.source_ranks[record.source]))
    if _AUTHORITY_ORDER.get(record.authority, 0) > _AUTHORITY_ORDER.get(artifact.authority, 0):
        artifact.authority = record.authority
    if _EVIDENCE_ORDER.get(record.evidence_level, 0) > _EVIDENCE_ORDER.get(artifact.evidence_level, 0):
        artifact.evidence_level = record.evidence_level
    for key, value in record.metadata.items():
        if value not in (None, "", [], {}):
            artifact.metadata.setdefault(key, value)
    artifact.source_count = 1


def deduplicate_artifacts(records: Iterable[ArtifactRecord]) -> list[Artifact]:
    artifacts: list[Artifact] = []
    index: dict[str, int] = {}
    for record in records:
        if not record.title:
            continue
        key = _key(record)
        match = index.get(key)
        if match is None:
            artifacts.append(_record_to_artifact(record))
            match = len(artifacts) - 1
            index[key] = match
        else:
            _merge(artifacts[match], record)
    return artifacts


def score_artifact(artifact: Artifact, *, rrf_k: int = _RRF_K) -> float:
    score = 0.0
    for ranks in artifact.source_ranks.values():
        for rank in set(ranks):
            score += 1.0 / (rrf_k + max(rank, 1))
    artifact.fusion_score = score
    return score


def rank_artifacts(artifacts: list[Artifact]) -> list[Artifact]:
    for artifact in artifacts:
        score_artifact(artifact)
    ranked = sorted(artifacts, key=lambda item: item.title.casefold())
    ranked = sorted(ranked, key=lambda item: item.published_at or "0000-00-00", reverse=True)
    ranked = sorted(ranked, key=lambda item: _AUTHORITY_ORDER.get(item.authority, 0), reverse=True)
    ranked = sorted(ranked, key=lambda item: item.fusion_score, reverse=True)
    return ranked
