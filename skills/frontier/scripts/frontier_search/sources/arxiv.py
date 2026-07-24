"""arXiv Atom API search adapter."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from urllib.parse import urlencode

from ..models import SearchRequest, SearchResponse, SourceRecord
from ..normalize import clean_text, normalize_arxiv_id, normalize_date, normalize_doi
from ..transport import request_text

_ATOM = "http://www.w3.org/2005/Atom"
_ARXIV = "http://arxiv.org/schemas/atom"


class ArxivAdapter:
    name = "arxiv"
    role = "scholarly"
    endpoint = "https://export.arxiv.org/api/query"

    def search(self, query: str, request: SearchRequest) -> SearchResponse:
        # Restrict to all fields while keeping query construction conservative.
        search_query = f'all:"{query.replace(chr(34), "")}"'
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": min(max(request.per_source_limit, 1), 100),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = f"{self.endpoint}?{urlencode(params)}"
        xml_payload = request_text(url, timeout=request.timeout_seconds, max_retries=request.max_retries)
        papers = self.parse_results(xml_payload, query)
        return SearchResponse(source=self.name, query=query, status="ok", papers=papers)

    @staticmethod
    def parse_results(xml_payload: str, query: str) -> list[SourceRecord]:
        root = ET.fromstring(xml_payload)
        records: list[SourceRecord] = []
        for index, entry in enumerate(root.findall(f"{{{_ATOM}}}entry"), start=1):
            title = clean_text(entry.findtext(f"{{{_ATOM}}}title"))
            if not title:
                continue
            authors = [
                author_name
                for author_name in (
                    clean_text(author.findtext(f"{{{_ATOM}}}name"))
                    for author in entry.findall(f"{{{_ATOM}}}author")
                )
                if author_name
            ]
            raw_id = clean_text(entry.findtext(f"{{{_ATOM}}}id"))
            arxiv_id = normalize_arxiv_id(raw_id)
            urls: list[str] = []
            if raw_id:
                urls.append(raw_id)
            for link in entry.findall(f"{{{_ATOM}}}link"):
                href = clean_text(link.attrib.get("href"))
                if href and href not in urls:
                    urls.append(href)
            doi = normalize_doi(entry.findtext(f"{{{_ARXIV}}}doi"))
            journal_ref = clean_text(entry.findtext(f"{{{_ARXIV}}}journal_ref"))
            categories = [
                category.attrib.get("term", "")
                for category in entry.findall(f"{{{_ARXIV}}}primary_category")
                if category.attrib.get("term")
            ]
            records.append(
                SourceRecord(
                    source="arxiv",
                    query=query,
                    source_rank=index,
                    title=title,
                    authors=authors,
                    abstract=clean_text(entry.findtext(f"{{{_ATOM}}}summary")),
                    published_at=normalize_date(entry.findtext(f"{{{_ATOM}}}published")),
                    updated_at=normalize_date(entry.findtext(f"{{{_ATOM}}}updated")),
                    doi=doi,
                    arxiv_id=arxiv_id,
                    venue="arXiv",
                    publication_status="preprint",
                    urls=urls,
                    metadata={
                        "journal_ref": journal_ref,
                        "categories": categories,
                    },
                )
            )
        return records
