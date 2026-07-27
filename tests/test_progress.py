from __future__ import annotations

import io
import threading
import time
import unittest
from datetime import date

from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.models import SearchRequest, SearchResponse, SourceRecord  # noqa: E402
from frontier_search.progress import ProgressEvent  # noqa: E402
from frontier_search.search import run_search  # noqa: E402
from frontier_search.ui import ProgressDisplay  # noqa: E402


class DelayedAdapter:
    role = "scholarly"

    def __init__(self, name: str, delay: float, status: str = "ok") -> None:
        self.name = name
        self.delay = delay
        self.status = status

    def search(self, query: str, request: SearchRequest) -> SearchResponse:
        time.sleep(self.delay)
        papers = []
        if self.status == "ok":
            papers.append(
                SourceRecord(
                    source=self.name,
                    query=query,
                    source_rank=1,
                    title=f"{self.name} result",
                    published_at="2026-02-01",
                )
            )
        return SearchResponse(
            source=self.name,
            query=query,
            status=self.status,
            papers=papers,
            error="provider unavailable" if self.status != "ok" else None,
        )


class ConcurrencyTrackingAdapter(DelayedAdapter):
    max_concurrency = 1

    def __init__(self) -> None:
        super().__init__("serial", 0.01)
        self.active = 0
        self.max_active = 0
        self.lock = threading.Lock()

    def search(self, query: str, request: SearchRequest) -> SearchResponse:
        with self.lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
        try:
            return super().search(query, request)
        finally:
            with self.lock:
                self.active -= 1


class InteractiveStream(io.StringIO):
    def isatty(self) -> bool:
        return True


class ProgressTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = SearchRequest(
            queries=("frontier",),
            since=date(2026, 1, 1),
            until=date(2026, 3, 1),
        )

    def test_provider_events_arrive_in_completion_order(self) -> None:
        events: list[ProgressEvent] = []
        run_search(
            self.request,
            adapters=[
                DelayedAdapter("slow", 0.03),
                DelayedAdapter("fast", 0.001),
            ],
            momentum_adapters=[],
            on_progress=events.append,
        )

        finished = [
            event.source
            for event in events
            if event.name == "provider_finished"
        ]
        self.assertEqual(finished, ["fast", "slow"])
        self.assertEqual(events[0].name, "run_started")
        self.assertEqual(
            events[0].counts,
            {
                "providers": 2,
                "queries": 1,
                "tasks": 2,
                "scholarly_providers": 2,
                "momentum_providers": 0,
            },
        )
        self.assertEqual(events[-1].name, "run_finished")

    def test_renderer_failures_do_not_break_search(self) -> None:
        def broken_renderer(_event: ProgressEvent) -> None:
            raise RuntimeError("terminal closed")

        run = run_search(
            self.request,
            adapters=[DelayedAdapter("openalex", 0)],
            momentum_adapters=[],
            on_progress=broken_renderer,
        )
        self.assertEqual(run.counts["returned"], 1)

    def test_adapter_concurrency_limit_is_respected(self) -> None:
        adapter = ConcurrencyTrackingAdapter()
        request = SearchRequest(
            queries=("anchor", "lexical expansion", "adjacent mechanism"),
            since=date(2026, 1, 1),
            until=date(2026, 3, 1),
        )

        run_search(
            request,
            adapters=[adapter],
            momentum_adapters=[],
            on_progress=lambda _event: None,
        )

        self.assertEqual(adapter.max_active, 1)

    def test_plain_renderer_emits_compact_search_receipt(self) -> None:
        stream = io.StringIO()
        display = ProgressDisplay(stream)
        display(
            ProgressEvent(
                name="run_started",
                topic="physical AI",
                total=2,
                counts={
                    "providers": 1,
                    "queries": 1,
                    "tasks": 1,
                    "scholarly_providers": 1,
                    "momentum_providers": 0,
                },
            )
        )
        display(
            ProgressEvent(
                name="provider_started",
                source="openalex",
                role="scholarly",
                state="running",
                total=1,
            )
        )
        display(
            ProgressEvent(
                name="provider_finished",
                source="openalex",
                role="scholarly",
                state="completed",
                query="physical AI",
                completed=1,
                total=1,
                result_count=4,
                duration_ms=120,
            )
        )
        display(
            ProgressEvent(
                name="run_finished",
                state="completed",
                result_count=4,
                counts={"deduplicated": 4, "returned": 4},
                elapsed_ms=250,
            )
        )

        output = stream.getvalue()
        self.assertEqual(len(output.splitlines()), 4)
        self.assertIn("/frontier · paper search complete", output)
        self.assertIn("OpenAlex", output)
        self.assertIn("4 matches", output)
        self.assertIn("Unique in window", output)
        self.assertIn("Shortlisted", output)
        self.assertNotIn("physical AI", output)
        self.assertNotIn("\033[", output)

    def test_receipt_discloses_source_state_without_raw_error(self) -> None:
        stream = io.StringIO()
        display = ProgressDisplay(stream)
        display(
            ProgressEvent(
                name="run_started",
                counts={
                    "providers": 1,
                    "queries": 2,
                    "tasks": 2,
                    "scholarly_providers": 1,
                    "momentum_providers": 0,
                },
            )
        )
        display(
            ProgressEvent(
                name="provider_finished",
                source="arxiv",
                role="scholarly",
                state="rate-limited",
                result_count=0,
                error="private provider error",
            )
        )
        display(
            ProgressEvent(
                name="run_finished",
                state="completed",
                counts={"deduplicated": 0, "returned": 0},
            )
        )

        output = stream.getvalue()
        self.assertIn("arXiv", output)
        self.assertIn("rate-limited", output)
        self.assertNotIn("private provider error", output)

    def test_interactive_renderer_replaces_status_with_receipt(self) -> None:
        stream = InteractiveStream()
        display = ProgressDisplay(stream)
        with patch.object(display, "_start_spinner"):
            display(
                ProgressEvent(
                    name="run_started",
                    topic="private query",
                    counts={
                        "providers": 1,
                        "queries": 3,
                        "tasks": 3,
                        "scholarly_providers": 1,
                        "momentum_providers": 0,
                    },
                )
            )
            display(
                ProgressEvent(
                    name="provider_finished",
                    source="openalex",
                    role="scholarly",
                    state="completed",
                    result_count=7,
                )
            )
            display(
                ProgressEvent(
                    name="run_finished",
                    state="completed",
                    counts={"deduplicated": 5, "returned": 3},
                )
            )

        receipt = stream.getvalue().rsplit("\r\033[2K", maxsplit=1)[-1]
        self.assertIn("/frontier", receipt)
        self.assertIn("OpenAlex", receipt)
        self.assertIn("7 matches", receipt)
        self.assertIn("Unique in window", receipt)
        self.assertNotIn("private query", receipt)

    def test_event_serialization_is_json_compatible(self) -> None:
        event = ProgressEvent(
            name="provider_finished",
            source="huggingface_papers",
            role="momentum",
            state="rate-limited",
            counts={"returned": 0},
        )
        payload = event.to_dict()
        self.assertEqual(payload["source"], "huggingface_papers")
        self.assertEqual(payload["counts"], {"returned": 0})


if __name__ == "__main__":
    unittest.main()
