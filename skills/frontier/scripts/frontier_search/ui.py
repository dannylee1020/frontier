"""Automatic terminal progress rendering for Frontier searches."""

from __future__ import annotations

from collections import Counter
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


@dataclass
class _ProviderState:
    source: str
    state: str = "queued"


class ProgressDisplay:
    """Render one quiet status line with automatic TTY/plain-text selection.

    Detailed provider lifecycle events remain available to structured sinks.
    Human output deliberately omits query text, provider rows, and raw errors.
    """

    def __init__(self, stream=None) -> None:
        self.stream = stream or sys.stderr
        self._interactive = self._supports_live_display()
        self._colored = self._interactive and not os.environ.get("NO_COLOR")
        self._rows: dict[str, _ProviderState] = {}
        self._started_at = time.monotonic()
        self._frame = 0
        self._phase = "collecting research sources"
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
        return (
            f"{self._style(Colors.CYAN, frame)} "
            f"{self._style(Colors.CYAN, '/frontier')} · "
            f"{self._style(Colors.DIM, self._phase)}"
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

    def _source_health(self) -> str:
        counts = Counter(row.state for row in self._rows.values())
        labels = (
            ("completed", "complete"),
            ("partial", "partial"),
            ("rate-limited", "rate-limited"),
            ("failed", "failed"),
            ("cancelled", "cancelled"),
        )
        parts = [
            f"{counts[state]} {label}"
            for state, label in labels
            if counts[state]
        ]
        return f"sources {', '.join(parts)}" if parts else "sources unavailable"

    def handle(self, event: ProgressEvent) -> None:
        with self._lock:
            if event.name == "run_started":
                self._rows.clear()
                self._started_at = time.monotonic()
                self._phase = "collecting research sources"
                if self._interactive:
                    self._start_spinner()
                    self._draw_live()
                return

            if event.source:
                row = self._rows.setdefault(
                    event.source,
                    _ProviderState(source=event.source),
                )
                row.state = event.state or row.state

            if event.name in {
                "provider_started",
                "provider_progress",
                "provider_finished",
            }:
                if self._interactive:
                    self._draw_live()
            elif event.name == "processing_started":
                self._phase = "processing and ranking"
                if self._interactive:
                    self._draw_live()
            elif event.name == "run_finished":
                self._stop_spinner()
                returned = event.counts.get("returned", event.result_count)
                date_filtered = event.counts.get("date_filtered")
                count_text = f"{returned} papers"
                if date_filtered is not None and date_filtered != returned:
                    count_text = f"{date_filtered} papers · {returned} returned"
                message = (
                    f"{self._style(Colors.GREEN, '✓')} "
                    f"{self._style(Colors.CYAN, '/frontier')} · "
                    f"research collected · {count_text} · {self._source_health()}"
                )
                if self._interactive:
                    self._draw_live(message)
                    self._write("\n")
                else:
                    self._plain(message)
            elif event.name == "run_cancelled":
                self._stop_spinner()
                message = "- /frontier · research cancelled"
                if self._interactive:
                    self._draw_live(message)
                    self._write("\n")
                else:
                    self._plain(message)
