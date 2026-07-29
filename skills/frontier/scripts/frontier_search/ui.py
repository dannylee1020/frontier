"""Automatic terminal progress rendering for Frontier searches."""

from __future__ import annotations

import os
import sys
import threading
import time
from dataclasses import dataclass

from .progress import ProgressEvent


class Colors:
    """Small ANSI palette used only for interactive terminal output."""

    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    RESET = "\033[0m"


SPINNER_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
SOURCE_LABELS = {
    "openalex": "OpenAlex",
    "arxiv": "arXiv",
    "semantic_scholar": "Semantic Scholar",
    "huggingface_papers": "Hugging Face Papers",
    "x_recent": "X",
}


@dataclass
class _ProviderState:
    source: str
    role: str = "scholarly"
    state: str = "queued"
    result_count: int = 0


class ProgressDisplay:
    """Render quiet live status followed by a compact search receipt.

    Detailed provider lifecycle events remain available to structured sinks.
    Human output deliberately omits query text and raw errors.
    """

    def __init__(self, stream=None) -> None:
        self.stream = stream or sys.stderr
        self._interactive = self._supports_live_display()
        self._colored = self._interactive and not os.environ.get("NO_COLOR")
        self._rows: dict[str, _ProviderState] = {}
        self._started_at = time.monotonic()
        self._frame = 0
        self._phase = "searching"
        self._lock = threading.RLock()
        self._running = False
        self._spinner_thread: threading.Thread | None = None

    def __call__(self, event: ProgressEvent) -> None:
        self.handle(event)

    def _supports_live_display(self) -> bool:
        if os.environ.get("TERM") == "dumb":
            return False
        try:
            return bool(self.stream.isatty())
        except (AttributeError, OSError):
            return False

    def _write(self, text: str) -> None:
        try:
            self.stream.write(text)
            self.stream.flush()
        except (BrokenPipeError, OSError):
            self._interactive = False

    def _style(self, color: str, text: str) -> str:
        if not self._colored:
            return text
        return f"{color}{text}{Colors.RESET}"

    def _status_line(self) -> str:
        frame = SPINNER_FRAMES[self._frame % len(SPINNER_FRAMES)]
        details: list[str] = [self._phase]
        if self._rows:
            matches = sum(row.result_count for row in self._rows.values())
            finished = sum(
                row.state not in {"queued", "running"}
                for row in self._rows.values()
            )
            if matches:
                details.append(f"{matches} matches")
            if finished:
                details.append(f"{finished}/{len(self._rows)} sources")
        return (
            f"{self._style(Colors.CYAN, frame)} "
            f"{self._style(Colors.CYAN, '/frontier')} · "
            f"{self._style(Colors.DIM, ' · '.join(details))}"
        )

    def _draw_live(self, message: str | None = None) -> None:
        self._write(f"\r\033[2K{message or self._status_line()}")

    def _spin(self) -> None:
        while self._running:
            with self._lock:
                if not self._running:
                    break
                self._frame += 1
                self._draw_live()
            time.sleep(0.12)

    def _start_spinner(self) -> None:
        if not self._interactive or self._running:
            return
        self._running = True
        self._spinner_thread = threading.Thread(target=self._spin, daemon=True)
        self._spinner_thread.start()

    def _stop_spinner(self) -> None:
        self._running = False
        if self._spinner_thread is not None:
            self._spinner_thread.join(timeout=0.5)
            self._spinner_thread = None

    def _plain(self, text: str) -> None:
        self._write(f"{text}\n")

    @staticmethod
    def _plural(count: int, singular: str, plural: str | None = None) -> str:
        return singular if count == 1 else (plural or f"{singular}s")

    def _receipt(self, counts: dict[str, int]) -> str:
        rows: list[str] = []
        for row in self._rows.values():
            label = SOURCE_LABELS.get(
                row.source,
                row.source.replace("_", " ").title(),
            )
            noun = (
                self._plural(row.result_count, "post", "posts")
                if row.role == "social_momentum"
                else self._plural(row.result_count, "match", "matches")
            )
            status = "" if row.state == "completed" else f" · {row.state}"
            rows.append(f"{label:<20} {row.result_count:>3} {noun}{status}")

        if any(row.role == "social_momentum" for row in self._rows.values()):
            x_posts = counts.get("returned_x", 0)
            x_trends = counts.get("x_trends", 0)
            rows.append(
                f"{'X posts (deduped)':<20} {x_posts:>3} "
                f"{self._plural(x_posts, 'post', 'posts')}"
            )
            rows.append(
                f"{'X trend clusters':<20} {x_trends:>3} "
                f"{self._plural(x_trends, 'cluster', 'clusters')}"
            )

        unique = counts.get("deduplicated", 0)
        returned = counts.get("returned", 0)
        unique_noun = self._plural(unique, "paper")
        shortlist_noun = self._plural(returned, "paper")
        rows.extend(
            (
                f"{'Unique in window':<20} {unique:>3} {unique_noun}",
                f"{'Shortlisted':<20} {returned:>3} {shortlist_noun}",
            )
        )

        rendered_rows = [
            f"{'└─' if index == len(rows) - 1 else '├─'} {row}"
            for index, row in enumerate(rows)
        ]
        has_x = any(row.role == "social_momentum" for row in self._rows.values())
        label = "search complete" if has_x else "paper search complete"
        header = (
            f"{self._style(Colors.GREEN, '✓')} "
            f"{self._style(Colors.CYAN, '/frontier')} · {label}"
        )
        return "\n".join((header, *rendered_rows))

    def handle(self, event: ProgressEvent) -> None:
        with self._lock:
            if event.name == "run_started":
                self._rows.clear()
                self._started_at = time.monotonic()
                angles = event.counts.get("queries", 0)
                scholarly = event.counts.get("scholarly_providers", 0)
                momentum = event.counts.get("momentum_providers", 0)
                parts: list[str] = []
                if angles:
                    parts.append(
                        f"searching {angles} {self._plural(angles, 'angle')}"
                    )
                if scholarly:
                    parts.append(
                        f"{scholarly} paper "
                        f"{self._plural(scholarly, 'index', 'indexes')}"
                    )
                if momentum:
                    parts.append(
                        f"{momentum} momentum {self._plural(momentum, 'feed')}"
                    )
                self._phase = " · ".join(parts) or "searching"
                if self._interactive:
                    self._start_spinner()
                    self._draw_live()
                return

            if event.source:
                row = self._rows.setdefault(
                    event.source,
                    _ProviderState(source=event.source, role=event.role or "scholarly"),
                )
                row.role = event.role or row.role
                row.state = event.state or row.state
                row.result_count = event.result_count

            if event.name in {
                "provider_started",
                "provider_progress",
                "provider_finished",
            }:
                if self._interactive:
                    self._draw_live()
            elif event.name == "processing_started":
                matches = sum(row.result_count for row in self._rows.values())
                self._phase = f"deduplicating and ranking {matches} matches"
                if self._interactive:
                    self._draw_live()
            elif event.name == "run_finished":
                self._stop_spinner()
                if self._interactive:
                    self._write("\r\033[2K")
                self._plain(self._receipt(event.counts))
            elif event.name == "run_cancelled":
                self._stop_spinner()
                message = "- /frontier · research cancelled"
                if self._interactive:
                    self._draw_live(message)
                    self._write("\n")
                else:
                    self._plain(message)
