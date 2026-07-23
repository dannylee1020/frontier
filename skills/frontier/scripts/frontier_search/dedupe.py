"""Conservative cross-provider paper deduplication."""

from __future__ import annotations

from typing import Iterable

from .models import Paper, SourceRecord, merge_unique
from .normalize import (
    clean_text,
    evidence_level_for,
    first_author_key,
    normalize_arxiv_id,
    normalize_doi,
    normalize_title,
    year_for,
)

_STATUS_PRIORITY = {
    "unknown": 0,
    "preprint": 20,
    "submitted": 30,
    "accepted": 40,
    "published": 50,
    "peer-reviewed": 50,
    "corrected": 55,
    "retracted": 100,
}


def _identifier_keys(record: SourceRecord | Paper) -> list[str]:
    keys: list[str] = []
    doi = normalize_doi(record.doi)
    arxiv_id = normalize_arxiv_id(record.arxiv_id)
    semantic_id = clean_text(record.semantic_scholar_id)
    if doi:
        keys.append(f"doi:{doi}")
    if arxiv_id:
        keys.append(f"arxiv:{arxiv_id}")
    if semantic_id:
        keys.append(f"semantic_scholar:{semantic_id}")
    return keys


def paper_from_record(record: SourceRecord) -> Paper:
    abstract = clean_text(record.abstract)
    paper = Paper(
        title=clean_text(record.title) or "Untitled paper",
        authors=[clean_text(author) or "" for author in record.authors if clean_text(author)],
        abstract=abstract,
        published_at=record.published_at,
        updated_at=record.updated_at,
        doi=normalize_doi(record.doi),
        arxiv_id=normalize_arxiv_id(record.arxiv_id),
        semantic_scholar_id=clean_text(record.semantic_scholar_id),
        venue=clean_text(record.venue),
        publication_status=record.publication_status or "unknown",
        urls=list(record.urls),
        sources=[record.source],
        matched_queries=[record.query],
        source_ranks={record.source: [record.source_rank]},
        source_scores=(
            {record.source: [record.source_score]}
            if record.source_score is not None
            else {}
        ),
        source_identifiers={
            record.source: [key.split(":", 1)[1] for key in _identifier_keys(record)]
        },
        evidence_level=evidence_level_for(abstract),
        title_key=normalize_title(record.title),
    )
    paper.source_count = 1
    return paper


def _compatible_title_match(left: Paper, right: SourceRecord) -> bool:
    if not left.title_key or left.title_key != normalize_title(right.title):
        return False
    left_author = first_author_key(left.authors)
    right_author = first_author_key(right.authors)
    if left_author and right_author and left_author != right_author:
        return False
    left_year = year_for(left)
    right_year = year_for(right)
    if left_year and right_year and abs(left_year - right_year) > 1:
        return False
    return True


def _choose_value(current: str | None, incoming: str | None) -> str | None:
    current = clean_text(current)
    incoming = clean_text(incoming)
    if not current:
        return incoming
    if not incoming:
        return current
    return current


def _earliest_date(current: str | None, incoming: str | None) -> str | None:
    values = [value for value in (current, incoming) if value]
    return min(values) if values else None


def _latest_date(current: str | None, incoming: str | None) -> str | None:
    values = [value for value in (current, incoming) if value]
    return max(values) if values else None


def _merge_record(paper: Paper, record: SourceRecord) -> None:
    if len(record.title) > len(paper.title):
        paper.title = clean_text(record.title) or paper.title
        paper.title_key = normalize_title(paper.title)
    if len(record.authors) > len(paper.authors):
        paper.authors = [clean_text(author) or "" for author in record.authors if clean_text(author)]
    if record.abstract and (not paper.abstract or len(record.abstract) > len(paper.abstract)):
        paper.abstract = clean_text(record.abstract)
    # The earliest public version is useful for a recency-bounded frontier search.
    paper.published_at = _earliest_date(paper.published_at, record.published_at)
    paper.updated_at = _latest_date(paper.updated_at, record.updated_at)
    paper.doi = _choose_value(paper.doi, normalize_doi(record.doi))
    paper.arxiv_id = _choose_value(paper.arxiv_id, normalize_arxiv_id(record.arxiv_id))
    paper.semantic_scholar_id = _choose_value(
        paper.semantic_scholar_id, clean_text(record.semantic_scholar_id)
    )
    paper.venue = _choose_value(paper.venue, record.venue)
    if _STATUS_PRIORITY.get(record.publication_status, 0) > _STATUS_PRIORITY.get(
        paper.publication_status, 0
    ):
        paper.publication_status = record.publication_status
    merge_unique(paper.urls, record.urls)
    merge_unique(paper.sources, [record.source])
    merge_unique(paper.matched_queries, [record.query])
    paper.source_ranks.setdefault(record.source, []).append(record.source_rank)
    paper.source_ranks[record.source] = sorted(set(paper.source_ranks[record.source]))
    if record.source_score is not None:
        paper.source_scores.setdefault(record.source, []).append(record.source_score)
    paper.source_identifiers.setdefault(record.source, [])
    for key in _identifier_keys(record):
        value = key.split(":", 1)[1]
        if value not in paper.source_identifiers[record.source]:
            paper.source_identifiers[record.source].append(value)
    paper.evidence_level = evidence_level_for(paper.abstract)
    paper.source_count = len(paper.sources)


def deduplicate(records: Iterable[SourceRecord]) -> list[Paper]:
    """Merge records with exact IDs, then conservative title/author/year matching."""

    papers: list[Paper] = []
    identifier_index: dict[str, int] = {}

    for record in records:
        if not clean_text(record.title):
            continue
        match_index: int | None = None
        for key in _identifier_keys(record):
            if key in identifier_index:
                match_index = identifier_index[key]
                break
        if match_index is None:
            for index, existing in enumerate(papers):
                if _compatible_title_match(existing, record):
                    match_index = index
                    break

        if match_index is None:
            papers.append(paper_from_record(record))
            match_index = len(papers) - 1
        else:
            _merge_record(papers[match_index], record)

        paper = papers[match_index]
        for key in _identifier_keys(paper):
            identifier_index[key] = match_index

    for paper in papers:
        paper.source_count = len(paper.sources)
    return papers
