"""Normalization helpers shared by all providers."""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Any

from .models import Paper, SourceRecord

_DOI_PREFIX = re.compile(r"^https?://(?:dx\.)?doi\.org/", re.IGNORECASE)
_ARXIV_PREFIX = re.compile(r"^(?:https?://)?(?:export\.)?arxiv\.org/(?:abs|pdf)/", re.IGNORECASE)
_WHITESPACE = re.compile(r"\s+")


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = _WHITESPACE.sub(" ", str(value).replace("\x00", " ")).strip()
    return text or None


def normalize_doi(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    text = _DOI_PREFIX.sub("", text).strip().rstrip(".,);]")
    if text.lower().startswith("doi:"):
        text = text[4:].strip()
    return text.lower() or None


def normalize_arxiv_id(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    text = _ARXIV_PREFIX.sub("", text)
    text = text.split("?")[0].split("#")[0].strip()
    text = text.removesuffix(".pdf").strip().rstrip("/")
    if text.lower().startswith("arxiv:"):
        text = text[6:].strip()
    # arXiv versions are document versions, not separate identity records.
    text = re.sub(r"v\d+$", "", text, flags=re.IGNORECASE)
    return text or None


def normalize_semantic_scholar_id(value: Any) -> str | None:
    text = clean_text(value)
    return text or None


def normalize_title(value: Any) -> str:
    text = clean_text(value) or ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(character for character in text if not unicodedata.combining(character))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return _WHITESPACE.sub(" ", text).strip()


def normalize_date(value: Any) -> str | None:
    """Return YYYY-MM-DD for common API date shapes."""

    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = clean_text(value)
    if not text:
        return None
    if len(text) == 4 and text.isdigit():
        return f"{text}-01-01"
    match = re.match(r"^(\d{4})[-/]?(\d{2})[-/]?(\d{2})", text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3))).isoformat()
        except ValueError:
            return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return None


def abstract_from_inverted_index(index: Any) -> str | None:
    """Reconstruct OpenAlex's token -> positions abstract representation."""

    if not isinstance(index, dict):
        return clean_text(index)
    words: dict[int, str] = {}
    for token, positions in index.items():
        if not isinstance(positions, list):
            continue
        for position in positions:
            try:
                words[int(position)] = str(token)
            except (TypeError, ValueError):
                continue
    if not words:
        return None
    return clean_text(" ".join(words[position] for position in sorted(words)))


def first_author_key(authors: list[str]) -> str | None:
    if not authors:
        return None
    return normalize_title(authors[0]) or None


def year_for(paper: Paper | SourceRecord) -> int | None:
    published = normalize_date(paper.published_at)
    if not published:
        return None
    return int(published[:4])


def evidence_level_for(abstract: str | None) -> str:
    return "abstract-level" if clean_text(abstract) else "metadata-only"
