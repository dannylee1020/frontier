"""Structured progress events for the Frontier search pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal


ProgressEventName = Literal[
    "run_started",
    "provider_started",
    "provider_progress",
    "provider_finished",
    "processing_started",
    "run_finished",
    "run_cancelled",
]
ProgressState = Literal[
    "queued",
    "running",
    "completed",
    "partial",
    "failed",
    "rate-limited",
    "unavailable",
    "error",
    "cancelled",
]


@dataclass(frozen=True)
class ProgressEvent:
    """A renderer-neutral update emitted while a search is running."""

    name: ProgressEventName
    topic: str | None = None
    source: str | None = None
    role: str | None = None
    state: ProgressState | None = None
    query: str | None = None
    completed: int = 0
    total: int = 0
    result_count: int = 0
    duration_ms: int | None = None
    elapsed_ms: int | None = None
    error: str | None = None
    counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation for host integrations."""

        return {
            "name": self.name,
            "topic": self.topic,
            "source": self.source,
            "role": self.role,
            "state": self.state,
            "query": self.query,
            "completed": self.completed,
            "total": self.total,
            "result_count": self.result_count,
            "duration_ms": self.duration_ms,
            "elapsed_ms": self.elapsed_ms,
            "error": self.error,
            "counts": dict(self.counts),
        }


ProgressSink = Callable[[ProgressEvent], None]


def emit_progress(sink: ProgressSink | None, event: ProgressEvent) -> None:
    """Deliver an event without allowing a renderer to break retrieval."""

    if sink is None:
        return
    try:
        sink(event)
    except Exception:
        # Progress is observational. A broken terminal or host callback must
        # never turn a provider result into a failed search.
        return


def summarize_provider_state(statuses: list[str]) -> ProgressState:
    """Map response statuses to the public provider-row state."""

    if not statuses or all(status == "ok" for status in statuses):
        return "completed"
    if all(status == "rate-limited" for status in statuses):
        return "rate-limited"
    if any(status == "ok" for status in statuses):
        return "partial"
    if any(status == "rate-limited" for status in statuses):
        return "partial"
    return "failed"
