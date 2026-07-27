"""Semantic Scholar Academic Graph search adapter."""

from __future__ import annotations

import os
from urllib.parse import urlencode

from ..models import SearchRequest, SearchResponse, SourceRecord
from ..normalize import clean_text, normalize_arxiv_id, normalize_date, normalize_doi
from ..transport import request_json


class SemanticScholarAdapter:
    name = "semantic_scholar"
    role = "scholarly"
    max_concurrency = 1
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
    fields = (
        "title,abstract,authors,year,publicationDate,venue,externalIds,url,"
        "openAccessPdf,fieldsOfStudy,isOpenAccess,publicationTypes"
    )

    @staticmethod
    def is_configured() -> bool:
        """Return whether authenticated Semantic Scholar access is configured."""

        return bool(os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "").strip())

    @staticmethod
    def _api_key() -> str:
        api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "SEMANTIC_SCHOLAR_API_KEY is required to use Semantic Scholar"
            )
        return api_key

    def search(self, query: str, request: SearchRequest) -> SearchResponse:
        api_key = self._api_key()
        params = {
            "query": query,
            "limit": min(max(request.per_source_limit, 1), 100),
            "offset": 0,
            "fields": self.fields,
            "year": f"{request.since.year}-{request.until.year}",
        }
        url = f"{self.endpoint}?{urlencode(params)}"
        payload = request_json(
            url,
            headers={"x-api-key": api_key},
            timeout=request.timeout_seconds,
            max_retries=request.max_retries,
        )
        raw_results = payload.get("data", [])
        if not isinstance(raw_results, list):
            raise ValueError("Semantic Scholar response did not contain a data list")
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
            for author in item.get("authors", []) or []:
                if isinstance(author, dict) and clean_text(author.get("name")):
                    authors.append(clean_text(author["name"]) or "")
            external_ids = item.get("externalIds") or {}
            doi = normalize_doi(external_ids.get("DOI"))
            arxiv_id = normalize_arxiv_id(external_ids.get("ArXiv"))
            paper_id = clean_text(item.get("paperId"))
            urls: list[str] = []
            for candidate in (
                item.get("url"),
                (item.get("openAccessPdf") or {}).get("url")
                if isinstance(item.get("openAccessPdf"), dict)
                else None,
            ):
                candidate = clean_text(candidate)
                if candidate and candidate not in urls:
                    urls.append(candidate)
            publication_types = item.get("publicationTypes") or []
            if arxiv_id and not publication_types:
                status = "preprint"
            elif "JournalArticle" in publication_types or "Conference" in publication_types:
                status = "published"
            else:
                status = "unknown"
            records.append(
                SourceRecord(
                    source="semantic_scholar",
                    query=query,
                    source_rank=index,
                    title=title,
                    authors=authors,
                    abstract=clean_text(item.get("abstract")),
                    published_at=normalize_date(item.get("publicationDate") or item.get("year")),
                    doi=doi,
                    arxiv_id=arxiv_id,
                    semantic_scholar_id=paper_id,
                    venue=clean_text(item.get("venue")),
                    publication_status=status,
                    urls=urls,
                    metadata={
                        "fields_of_study": item.get("fieldsOfStudy") or [],
                        "is_open_access": bool(item.get("isOpenAccess")),
                        "publication_types": publication_types,
                    },
                )
            )
        return records
