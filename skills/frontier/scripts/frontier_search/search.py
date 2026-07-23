"""Concurrent multi-provider search orchestration."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Iterable

from .artifacts import deduplicate_artifacts, rank_artifacts
from .dedupe import deduplicate
from .models import (
    ArtifactSearchResponse,
    SearchRequest,
    SearchResponse,
    SearchRun,
    SourceRecord,
    utc_now,
)
from .rank import rank_papers
from .sources import (
    ArxivAdapter,
    GitHubAdapter,
    HuggingFaceAdapter,
    OpenAlexAdapter,
    SemanticScholarAdapter,
)
from .sources.base import (
    ArtifactSourceAdapter,
    SourceAdapter,
    timed_artifact_search,
    timed_search,
)


def default_adapters() -> list[SourceAdapter]:
    return [OpenAlexAdapter(), ArxivAdapter(), SemanticScholarAdapter()]


def default_artifact_adapters() -> list[ArtifactSourceAdapter]:
    return [HuggingFaceAdapter(), GitHubAdapter()]


def _record_in_date_range(record: SourceRecord, since: date, until: date) -> bool:
    if not record.published_at:
        return False
    try:
        published = date.fromisoformat(record.published_at)
    except ValueError:
        return False
    return since <= published <= until


def _normalize_queries(queries: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for query in queries:
        cleaned = " ".join(str(query).split()).strip()
        key = cleaned.casefold()
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return tuple(result)


def run_search(
    request: SearchRequest,
    *,
    adapters: list[SourceAdapter] | None = None,
    artifact_adapters: list[ArtifactSourceAdapter] | None = None,
) -> SearchRun:
    queries = _normalize_queries(request.queries)
    if not queries:
        raise ValueError("At least one non-empty query is required")
    if request.since > request.until:
        raise ValueError("since must be on or before until")
    if (
        request.candidate_limit < 1
        or request.per_source_limit < 1
        or request.artifact_limit < 1
    ):
        raise ValueError("limits must be positive")

    providers = adapters or default_adapters()
    artifact_providers = (
        default_artifact_adapters() if artifact_adapters is None else artifact_adapters
    )
    paper_tasks: list[tuple[SourceAdapter, str]] = [
        (adapter, query) for adapter in providers for query in queries
    ]
    artifact_tasks: list[tuple[ArtifactSourceAdapter, str]] = [
        (adapter, query) for adapter in artifact_providers for query in queries
    ]
    responses: list[SearchResponse] = []
    artifact_responses: list[ArtifactSearchResponse] = []
    total_tasks = len(paper_tasks) + len(artifact_tasks)
    max_workers = min(max(total_tasks, 1), 16)
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="frontier-search") as pool:
        futures = [
            pool.submit(timed_search, adapter, query, request)
            for adapter, query in paper_tasks
        ]
        artifact_futures = [
            pool.submit(timed_artifact_search, adapter, query, request)
            for adapter, query in artifact_tasks
        ]
        for future in futures:
            responses.append(future.result())
        for future in artifact_futures:
            artifact_responses.append(future.result())

    # Completion order is intentionally nondeterministic; sort artifacts so
    # identical inputs produce stable JSON and fixture tests remain reproducible.
    responses.sort(key=lambda response: (response.source, response.query.casefold()))
    artifact_responses.sort(
        key=lambda response: (response.source, response.query.casefold())
    )
    raw_records = [record for response in responses for record in response.papers]
    filtered_records = [
        record
        for record in raw_records
        if _record_in_date_range(record, request.since, request.until)
    ]
    merged = deduplicate(filtered_records)
    ranked = rank_papers(merged)[: request.candidate_limit]

    raw_artifacts = [
        artifact
        for response in artifact_responses
        for artifact in response.artifacts
    ]
    filtered_artifacts = [
        artifact
        for artifact in raw_artifacts
        if _record_in_date_range(artifact, request.since, request.until)
    ]
    merged_artifacts = deduplicate_artifacts(filtered_artifacts)
    ranked_artifacts = rank_artifacts(merged_artifacts)[: request.artifact_limit]

    return SearchRun(
        request=SearchRequest(
            queries=queries,
            since=request.since,
            until=request.until,
            candidate_limit=request.candidate_limit,
            per_source_limit=request.per_source_limit,
            timeout_seconds=request.timeout_seconds,
            max_retries=request.max_retries,
            artifact_limit=request.artifact_limit,
        ),
        executed_at=utc_now(),
        responses=responses,
        papers=ranked,
        artifact_responses=artifact_responses,
        artifacts=ranked_artifacts,
        counts={
            "raw": len(raw_records),
            "date_filtered": len(filtered_records),
            "deduplicated": len(merged),
            "returned": len(ranked),
            "raw_artifacts": len(raw_artifacts),
            "date_filtered_artifacts": len(filtered_artifacts),
            "deduplicated_artifacts": len(merged_artifacts),
            "returned_artifacts": len(ranked_artifacts),
        },
    )
