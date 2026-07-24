"""Concurrent multi-provider paper search orchestration."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import Iterable

from .dedupe import deduplicate
from .models import SearchRequest, SearchResponse, SearchRun, SourceRecord, utc_now
from .rank import rank_papers
from .sources import (
    ArxivAdapter,
    HuggingFacePapersAdapter,
    OpenAlexAdapter,
    SemanticScholarAdapter,
)
from .sources.base import SourceAdapter, timed_search


def default_adapters() -> list[SourceAdapter]:
    """Return the three canonical scholarly search providers."""

    return [OpenAlexAdapter(), ArxivAdapter(), SemanticScholarAdapter()]


def default_momentum_adapters() -> list[SourceAdapter]:
    """Return paper-attention overlays kept separate from scholarly evidence."""

    return [HuggingFacePapersAdapter()]


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


def _run_task_groups(
    scholarly_adapters: list[SourceAdapter],
    momentum_adapters: list[SourceAdapter],
    queries: tuple[str, ...],
    request: SearchRequest,
) -> tuple[list[SearchResponse], list[SearchResponse]]:
    tasks = [
        (adapter, query, "scholarly")
        for adapter in scholarly_adapters
        for query in queries
    ] + [
        (adapter, query, "momentum")
        for adapter in momentum_adapters
        for query in queries
    ]
    if not tasks:
        return [], []
    with ThreadPoolExecutor(
        max_workers=min(max(len(tasks), 1), 16),
        thread_name_prefix="frontier-search",
    ) as pool:
        futures = [
            (pool.submit(timed_search, adapter, query, request), role)
            for adapter, query, role in tasks
        ]
        scholarly_responses: list[SearchResponse] = []
        momentum_responses: list[SearchResponse] = []
        for future, role in futures:
            response = future.result()
            response.role = role
            if role == "momentum":
                momentum_responses.append(response)
            else:
                scholarly_responses.append(response)
    scholarly_responses.sort(
        key=lambda response: (response.source, response.query.casefold())
    )
    momentum_responses.sort(
        key=lambda response: (response.source, response.query.casefold())
    )
    return scholarly_responses, momentum_responses


def run_search(
    request: SearchRequest,
    *,
    adapters: list[SourceAdapter] | None = None,
    momentum_adapters: list[SourceAdapter] | None = None,
) -> SearchRun:
    queries = _normalize_queries(request.queries)
    if not queries:
        raise ValueError("At least one non-empty query is required")
    if request.since > request.until:
        raise ValueError("since must be on or before until")
    if request.candidate_limit < 1 or request.per_source_limit < 1:
        raise ValueError("limits must be positive")

    scholarly_providers = adapters if adapters is not None else default_adapters()
    momentum_providers = (
        momentum_adapters
        if momentum_adapters is not None
        else default_momentum_adapters()
    )
    responses, momentum_responses = _run_task_groups(
        scholarly_providers, momentum_providers, queries, request
    )

    raw_records = [record for response in responses for record in response.papers]
    raw_momentum_records = [
        record for response in momentum_responses for record in response.papers
    ]
    filtered_records = [
        record
        for record in raw_records
        if _record_in_date_range(record, request.since, request.until)
    ]
    filtered_momentum_records = [
        record
        for record in raw_momentum_records
        if _record_in_date_range(record, request.since, request.until)
    ]
    merged = deduplicate([*filtered_records, *filtered_momentum_records])
    ranked = rank_papers(merged)[: request.candidate_limit]

    return SearchRun(
        request=SearchRequest(
            queries=queries,
            since=request.since,
            until=request.until,
            candidate_limit=request.candidate_limit,
            per_source_limit=request.per_source_limit,
            timeout_seconds=request.timeout_seconds,
            max_retries=request.max_retries,
        ),
        executed_at=utc_now(),
        responses=responses,
        momentum_responses=momentum_responses,
        papers=ranked,
        counts={
            "raw": len(raw_records) + len(raw_momentum_records),
            "date_filtered": len(filtered_records) + len(filtered_momentum_records),
            "raw_scholarly": len(raw_records),
            "date_filtered_scholarly": len(filtered_records),
            "raw_momentum": len(raw_momentum_records),
            "date_filtered_momentum": len(filtered_momentum_records),
            "deduplicated": len(merged),
            "returned": len(ranked),
        },
    )
