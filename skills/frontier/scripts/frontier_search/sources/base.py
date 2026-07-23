"""Provider adapter protocol and shared response timing."""

from __future__ import annotations

import time
from typing import Protocol

from ..models import ArtifactSearchResponse, SearchRequest, SearchResponse


class SourceAdapter(Protocol):
    name: str

    def search(self, query: str, request: SearchRequest) -> SearchResponse:
        ...


def timed_search(adapter: SourceAdapter, query: str, request: SearchRequest) -> SearchResponse:
    started = time.monotonic()
    try:
        response = adapter.search(query, request)
    except Exception as error:  # Provider failures are isolated by the orchestrator.
        response = SearchResponse(
            source=adapter.name,
            query=query,
            status="error",
            error=f"{type(error).__name__}: {error}",
        )
    response.duration_ms = round((time.monotonic() - started) * 1000)
    return response


class ArtifactSourceAdapter(Protocol):
    name: str

    def search(self, query: str, request: SearchRequest) -> ArtifactSearchResponse:
        ...


def timed_artifact_search(
    adapter: ArtifactSourceAdapter, query: str, request: SearchRequest
) -> ArtifactSearchResponse:
    started = time.monotonic()
    try:
        response = adapter.search(query, request)
    except Exception as error:  # Artifact failures are isolated by the orchestrator.
        response = ArtifactSearchResponse(
            source=adapter.name,
            query=query,
            status="error",
            error=f"{type(error).__name__}: {error}",
        )
    response.duration_ms = round((time.monotonic() - started) * 1000)
    return response
