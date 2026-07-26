"""Hugging Face trending-paper momentum adapter."""

from __future__ import annotations

import math
import threading
from urllib.parse import urlencode

from ..models import SearchRequest, SearchResponse, SourceRecord
from ..normalize import clean_text, normalize_arxiv_id, normalize_date, normalize_title
from ..transport import request_json_value


_STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def _query_terms(query: str) -> set[str]:
    return {
        term
        for term in normalize_title(query).split()
        if len(term) >= 3 and term not in _STOPWORDS
    }


def _is_relevant(title: str, summary: str | None, query: str) -> bool:
    """Apply a conservative local filter to the global HF feed.

    The daily-papers endpoint is a feed rather than a query API. Matching the
    title and summary locally prevents unrelated trending papers from entering
    a topic-scoped run while retaining papers that use only part of a query's
    terminology.
    """

    terms = _query_terms(query)
    if not terms:
        return False
    haystack = set(normalize_title(f"{title} {summary or ''}").split())
    overlap = len(terms & haystack)
    return overlap >= max(1, math.ceil(len(terms) / 3))


def _authors(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, dict):
            name = clean_text(item.get("name"))
        else:
            name = clean_text(item)
        if name:
            result.append(name)
    return result


def _paper_page(arxiv_id: str | None, raw_id: str | None) -> str | None:
    identifier = arxiv_id or clean_text(raw_id)
    return f"https://huggingface.co/papers/{identifier}" if identifier else None


class HuggingFacePapersAdapter:
    """Read the current Hugging Face Papers feed as a momentum overlay."""

    name = "huggingface_papers"
    role = "momentum"
    endpoint = "https://huggingface.co/api/daily_papers"

    def __init__(self) -> None:
        self._payload: list[object] | None = None
        self._payload_lock = threading.Lock()

    def _load_payload(self, request: SearchRequest) -> list[object]:
        with self._payload_lock:
            if self._payload is not None:
                return self._payload
            payload = request_json_value(
                f"{self.endpoint}?{urlencode({'limit': 50})}",
                headers={"Accept": "application/json"},
                timeout=request.timeout_seconds,
                max_retries=request.max_retries,
            )
            if not isinstance(payload, list):
                raise ValueError(
                    "Hugging Face Papers response did not contain a list"
                )
            self._payload = payload
            return payload

    def search(self, query: str, request: SearchRequest) -> SearchResponse:
        # The endpoint currently returns a bounded daily/trending feed. Keep
        # the query parameter-free, reuse it across discovery branches, and
        # perform topic matching locally.
        payload = self._load_payload(request)

        papers: list[SourceRecord] = []
        for feed_rank, item in enumerate(payload, start=1):
            if not isinstance(item, dict):
                continue
            nested = item.get("paper")
            paper = nested if isinstance(nested, dict) else item
            title = clean_text(paper.get("title") or item.get("title"))
            summary = clean_text(paper.get("summary") or item.get("summary"))
            if not title or not _is_relevant(title, summary, query):
                continue

            raw_id = clean_text(paper.get("id") or item.get("id"))
            arxiv_id = normalize_arxiv_id(raw_id)
            if not arxiv_id and not raw_id:
                continue
            published_raw = paper.get("publishedAt") or item.get("publishedAt")
            submitted_raw = (
                paper.get("submittedOnDailyAt")
                or item.get("submittedOnDailyAt")
                or item.get("submittedAt")
            )
            published_at = normalize_date(published_raw)
            observed_at = normalize_date(submitted_raw)
            page_url = _paper_page(arxiv_id, raw_id)
            urls = [page_url] if page_url else []
            if arxiv_id:
                urls.append(f"https://arxiv.org/abs/{arxiv_id}")
            project_page = clean_text(paper.get("projectPage") or item.get("projectPage"))
            if project_page and project_page not in urls:
                urls.append(project_page)

            organization = paper.get("organization") or item.get("organization")
            organization_name = None
            if isinstance(organization, dict):
                organization_name = clean_text(
                    organization.get("name") or organization.get("fullname")
                )
            papers.append(
                SourceRecord(
                    source=self.name,
                    query=query,
                    source_rank=feed_rank,
                    title=title,
                    authors=_authors(paper.get("authors") or item.get("authors")),
                    abstract=summary,
                    published_at=published_at,
                    updated_at=observed_at,
                    arxiv_id=arxiv_id,
                    venue="Hugging Face Papers",
                    publication_status="preprint" if arxiv_id else "unknown",
                    urls=urls,
                    metadata={
                        "momentum_signal": "huggingface-trending-papers",
                        "huggingface_rank": feed_rank,
                        "huggingface_upvotes": paper.get("upvotes")
                        if paper.get("upvotes") is not None
                        else item.get("upvotes"),
                        "submitted_on_daily_at": submitted_raw,
                        "momentum_observed_at": observed_at,
                        "organization": organization_name,
                        "paper_page_url": page_url,
                    },
                )
            )
            if len(papers) >= request.per_source_limit:
                break

        return SearchResponse(
            source=self.name,
            role=self.role,
            query=query,
            status="ok",
            papers=papers,
        )
