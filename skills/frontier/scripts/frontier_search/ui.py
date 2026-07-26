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
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[95m"
    RESET = "\033[0m"


SPINNER_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
SOURCE_META = {
    "openalex": ("OpenAlex", "Scholarly", Colors.CYAN),
    "arxiv": ("arXiv", "Scholarly", Colors.GREEN),
    "semantic_scholar": ("Semantic Scholar", "Scholarly", Colors.YELLOW),
    "huggingface_papers": ("Hugging Face", "Momentum", Colors.PURPLE),
}
STATE_SYMBOLS = {
    "queued": "○",
    "running": "…",
    "completed": "✓",
    "partial": "~",
    "failed": "✗",
    "rate-limited": "!",
    "cancelled": "-",
}


@dataclass
class _ProviderRow:
    source: str
    role: str
    state: str = "queued"
    completed: int = 0
    total: int = 0
    result_count: int = 0
    duration_ms: int | None = None
    error: str | None = None


class ProgressDisplay:
    """Render one provider row with automatic TTY/plain-text selection.

    The display is deliberately not configurable through the CLI. It chooses
    the safest presentation from the output stream's capabilities and always
    keeps progress on stderr.
    """

    def __init__(self, stream=None) -> None:
        self.stream = stream or sys.stderr
        self._interactive = self._supports_live_display()
        self._colored = self._interactive and not os.environ.get("NO_COLOR")
        self._rows: dict[str, _ProviderRow] = {}
        self._topic = "research"
        self._started_at = time.monotonic()
        self._rendered_lines = 0
        self._frame = 0
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

    def _meta(self, source: str, role: str | None = None) -> tuple[str, str, str]:
        default = (source.replace("_", " ").title(), role or "Source", Colors.CYAN)
        return SOURCE_META.get(source, default)

    def _row_text(self, row: _ProviderRow) -> str:
        label, role, color = self._meta(row.source, row.role)
        symbol = STATE_SYMBOLS.get(row.state, "·")
        if row.state in {"queued", "running"}:
            progress = f"{row.completed}/{row.total} queries" if row.total else "waiting"
            detail = f"{row.state} · {progress}"
        else:
            detail = f"{row.result_count} {self._result_noun(row.source)}"
            if row.duration_ms is not None:
                detail += f" · {row.duration_ms / 1000:.1f}s"
            if row.state != "completed":
                detail += f" · {row.state}"
        if row.error and row.state in {"failed", "rate-limited", "partial"}:
            detail += f" · {self._short_error(row.error)}"
        styled_symbol = self._style(self._state_color(row.state), symbol)
        styled_label = self._style(color, f"{label:<18}")
        return f"{styled_symbol} {styled_label} {detail}"

    @staticmethod
    def _result_noun(source: str) -> str:
        return "momentum matches" if source == "huggingface_papers" else "papers"

    @staticmethod
    def _short_error(error: str) -> str:
        compact = " ".join(error.split())
        return compact if len(compact) <= 72 else f"{compact[:69]}..."

    @staticmethod
    def _state_color(state: str) -> str:
        if state == "completed":
            return Colors.GREEN
        if state in {"failed", "rate-limited"}:
            return Colors.RED if state == "failed" else Colors.YELLOW
        if state == "partial":
            return Colors.YELLOW
        return Colors.CYAN

    def _lines(self, suffix: str | None = None) -> list[str]:
        frame = SPINNER_FRAMES[self._frame % len(SPINNER_FRAMES)]
        heading = f"{self._style(Colors.PURPLE, '/frontier')} · {self._style(Colors.DIM, f'researching {self._topic}')}"
        if self._interactive:
            heading = f"{self._style(Colors.CYAN, frame)} {heading}"
        lines = [heading]
        lines.extend(self._row_text(row) for row in self._rows.values())
        if suffix:
            lines.append(suffix)
        return lines

    def _draw_live(self, suffix: str | None = None) -> None:
        lines = self._lines(suffix)
        if self._rendered_lines:
            self._write(f"\033[{self._rendered_lines}A")
        for line in lines:
            self._write(f"\r\033[2K{line}\n")
        self._rendered_lines = len(lines)

    def _spin(self) -> None:
        while self._running:
            with self._lock:
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

    def _plain_provider(self, row: _ProviderRow) -> None:
        symbol = STATE_SYMBOLS.get(row.state, "·")
        label, _, _ = self._meta(row.source, row.role)
        if row.state in {"queued", "running"}:
            detail = f"{row.completed}/{row.total} queries"
        else:
            detail = f"{row.result_count} {self._result_noun(row.source)}"
            if row.duration_ms is not None:
                detail += f" · {row.duration_ms / 1000:.1f}s"
            if row.state != "completed":
                detail += f" · {row.state}"
            if row.error:
                detail += f" · {self._short_error(row.error)}"
        self._plain(f"{symbol} {label} {detail}")

    def handle(self, event: ProgressEvent) -> None:
        with self._lock:
            if event.name == "run_started":
                self._topic = event.topic or "research"
                self._started_at = time.monotonic()
                if self._interactive:
                    self._start_spinner()
                    self._draw_live()
                else:
                    self._plain(f"/frontier · researching {self._topic}")
                return

            if event.source:
                row = self._rows.setdefault(
                    event.source,
                    _ProviderRow(
                        source=event.source,
                        role=event.role or "source",
                    ),
                )
                row.role = event.role or row.role
                row.state = event.state or row.state
                row.completed = event.completed
                row.total = event.total
                row.result_count = event.result_count
                row.duration_ms = event.duration_ms
                row.error = event.error

            if event.name == "provider_started":
                if not self._interactive:
                    self._plain_provider(self._rows[event.source])
                else:
                    self._draw_live()
            elif event.name == "provider_progress":
                # Captured agent output stays low-noise: the final provider
                # row carries the aggregate result and failure state.
                if self._interactive:
                    self._draw_live()
            elif event.name == "provider_finished":
                if not self._interactive:
                    self._plain_provider(self._rows[event.source])
                else:
                    self._draw_live()
            elif event.name == "processing_started":
                if not self._interactive:
                    self._plain("… Processing and ranking results")
                else:
                    self._draw_live("… Processing and ranking results")
            elif event.name == "run_finished":
                self._stop_spinner()
                elapsed_ms = event.elapsed_ms
                if elapsed_ms is None:
                    elapsed_ms = round((time.monotonic() - self._started_at) * 1000)
                returned = event.counts.get("returned", event.result_count)
                date_filtered = event.counts.get("date_filtered")
                count_text = f"{returned} papers"
                if date_filtered is not None and date_filtered != returned:
                    count_text = f"{date_filtered} papers · {returned} returned"
                message = f"✓ Research complete · {count_text} · {elapsed_ms / 1000:.1f}s"
                if self._interactive:
                    self._draw_live(message)
                    self._write("\n")
                else:
                    self._plain(message)
            elif event.name == "run_cancelled":
                self._stop_spinner()
                message = "- Research cancelled"
                if self._interactive:
                    self._draw_live(message)
                    self._write("\n")
                else:
                    self._plain(message)
