"""Concurrent multi-provider paper search orchestration."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
import time
from typing import Iterable

from .dedupe import deduplicate
from .models import SearchRequest, SearchResponse, SearchRun, SourceRecord, utc_now
from .progress import ProgressEvent, ProgressSink, emit_progress, summarize_provider_state
from .ui import ProgressDisplay
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
    on_progress: ProgressSink,
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
    providers: dict[str, tuple[str, int]] = {}
    for adapter, _query, role in tasks:
        name = adapter.name
        current_role, total = providers.get(name, (role, 0))
        providers[name] = (current_role, total + 1)

    emit_progress(
        on_progress,
        ProgressEvent(
            name="run_started",
            topic=" / ".join(queries),
            completed=0,
            total=len(tasks),
            counts={"providers": len(providers), "queries": len(tasks)},
        ),
    )
    for source, (role, total) in providers.items():
        emit_progress(
            on_progress,
            ProgressEvent(
                name="provider_started",
                source=source,
                role=role,
                state="running",
                total=total,
            ),
        )
    if not tasks:
        return [], []

    provider_responses: dict[str, list[SearchResponse]] = {
        source: [] for source in providers
    }
    provider_completed: dict[str, int] = {source: 0 for source in providers}
    with ThreadPoolExecutor(
        max_workers=min(max(len(tasks), 1), 16),
        thread_name_prefix="frontier-search",
    ) as pool:
        future_tasks = {
            pool.submit(timed_search, adapter, query, request): (adapter, query, role)
            for adapter, query, role in tasks
        }
        scholarly_responses: list[SearchResponse] = []
        momentum_responses: list[SearchResponse] = []
        for future in as_completed(future_tasks):
            adapter, query, role = future_tasks[future]
            try:
                response = future.result()
            except Exception as error:  # Defensive isolation around executor failures.
                response = SearchResponse(
                    source=adapter.name,
                    query=query,
                    status="error",
                    error=f"{type(error).__name__}: {error}",
                    role=role,
                )
            response.role = role
            provider_responses.setdefault(response.source, []).append(response)
            provider_completed[response.source] = provider_completed.get(response.source, 0) + 1
            completed = provider_completed[response.source]
            total = providers.get(response.source, (role, completed))[1]
            responses = provider_responses[response.source]
            state = (
                summarize_provider_state([item.status for item in responses])
                if completed == total
                else "running"
            )
            event_name = "provider_finished" if completed == total else "provider_progress"
            emit_progress(
                on_progress,
                ProgressEvent(
                    name=event_name,
                    source=response.source,
                    role=role,
                    state=state,
                    query=response.query,
                    completed=completed,
                    total=total,
                    result_count=sum(len(item.papers) for item in responses),
                    duration_ms=(
                        max(item.duration_ms for item in responses) if responses else None
                    ),
                    error=next(
                        (item.error for item in reversed(responses) if item.error),
                        None,
                    ),
                ),
            )
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
    on_progress: ProgressSink | None = None,
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
    progress = on_progress if on_progress is not None else ProgressDisplay()
    started_at = time.monotonic()
    try:
        responses, momentum_responses = _run_task_groups(
            scholarly_providers,
            momentum_providers,
            queries,
            request,
            progress,
        )
    except KeyboardInterrupt:
        emit_progress(
            progress,
            ProgressEvent(
                name="run_cancelled",
                state="cancelled",
                elapsed_ms=round((time.monotonic() - started_at) * 1000),
            ),
        )
        raise

    emit_progress(
        progress,
        ProgressEvent(name="processing_started", state="running"),
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

    run = SearchRun(
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
    emit_progress(
        progress,
        ProgressEvent(
            name="run_finished",
            state="completed",
            result_count=len(ranked),
            elapsed_ms=round((time.monotonic() - started_at) * 1000),
            counts=run.counts,
        ),
    )
    return run
