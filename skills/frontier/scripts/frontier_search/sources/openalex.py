"""OpenAlex works search adapter."""

from __future__ import annotations

import os
from urllib.parse import urlencode

from ..models import SearchRequest, SearchResponse, SourceRecord
from ..normalize import (
    abstract_from_inverted_index,
    clean_text,
    normalize_arxiv_id,
    normalize_date,
    normalize_doi,
)
from ..transport import request_json


class OpenAlexAdapter:
    name = "openalex"
    endpoint = "https://api.openalex.org/works"

    def search(self, query: str, request: SearchRequest) -> SearchResponse:
        params = {
            "search": query,
            "filter": (
                f"from_publication_date:{request.since.isoformat()},"
                f"to_publication_date:{request.until.isoformat()}"
            ),
            "per-page": min(max(request.per_source_limit, 1), 200),
            "page": 1,
        }
        mailto = os.environ.get("OPENALEX_EMAIL")
        if mailto:
            params["mailto"] = mailto
        url = f"{self.endpoint}?{urlencode(params)}"
        payload = request_json(url, timeout=request.timeout_seconds, max_retries=request.max_retries)
        raw_results = payload.get("results", [])
        if not isinstance(raw_results, list):
            raise ValueError("OpenAlex response did not contain a results list")
        papers = self.parse_results(raw_results, query)
        return SearchResponse(source=self.name, query=query, status="ok", papers=papers)

    @staticmethod
    def parse_results(results: list[object], query: str) -> list[SourceRecord]:
        records: list[SourceRecord] = []
        for index, item in enumerate(results, start=1):
            if not isinstance(item, dict):
                continue
            title = clean_text(item.get("title"))
            if not title:
                continue
            authors: list[str] = []
            for authorship in item.get("authorships", []) or []:
                if isinstance(authorship, dict):
                    author = authorship.get("author") or {}
                    if isinstance(author, dict) and clean_text(author.get("display_name")):
                        authors.append(clean_text(author["display_name"]) or "")
            ids = item.get("ids") or {}
            primary_location = item.get("primary_location") or {}
            source = primary_location.get("source") or {}
            urls = []
            for candidate in (
                primary_location.get("landing_page_url"),
                primary_location.get("pdf_url"),
                item.get("id"),
            ):
                candidate = clean_text(candidate)
                if candidate and candidate not in urls:
                    urls.append(candidate)
            is_retracted = bool(item.get("is_retracted"))
            work_type = clean_text(item.get("type"))
            if is_retracted:
                status = "retracted"
            elif work_type == "preprint":
                status = "preprint"
            else:
                status = "published"
            records.append(
                SourceRecord(
                    source="openalex",
                    query=query,
                    source_rank=index,
                    title=title,
                    authors=authors,
                    abstract=abstract_from_inverted_index(item.get("abstract_inverted_index")),
                    published_at=normalize_date(item.get("publication_date")),
                    updated_at=None,
                    doi=normalize_doi(item.get("doi") or ids.get("doi")),
                    arxiv_id=normalize_arxiv_id(ids.get("arxiv")),
                    venue=clean_text(source.get("display_name")),
                    publication_status=status,
                    urls=urls,
                    source_score=(
                        float(item["relevance_score"])
                        if isinstance(item.get("relevance_score"), (int, float))
                        else None
                    ),
                    metadata={
                        "openalex_id": clean_text(item.get("id")),
                        "open_access": bool((item.get("open_access") or {}).get("is_oa"))
                        if isinstance(item.get("open_access"), dict)
                        else None,
                    },
                )
            )
        return records
