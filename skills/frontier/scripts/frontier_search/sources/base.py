"""Provider adapter protocol and shared response timing."""

from __future__ import annotations

import time
from typing import Protocol

from ..models import SearchRequest, SearchResponse


class SourceAdapter(Protocol):
    name: str
    role: str

    def search(self, query: str, request: SearchRequest) -> SearchResponse:
        ...


def timed_search(adapter: SourceAdapter, query: str, request: SearchRequest) -> SearchResponse:
    started = time.monotonic()
    try:
        response = adapter.search(query, request)
    except Exception as error:  # Provider failures are isolated by the orchestrator.
        status = "rate-limited" if getattr(error, "status_code", None) == 429 else "error"
        response = SearchResponse(
            source=adapter.name,
            role=getattr(adapter, "role", "scholarly"),
            query=query,
            status=status,
            error=f"{type(error).__name__}: {error}",
        )
    response.duration_ms = round((time.monotonic() - started) * 1000)
    return response
