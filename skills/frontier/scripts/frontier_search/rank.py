"""Provider-independent ranking for merged candidates."""

from __future__ import annotations

from datetime import date

from .models import Paper

_RRF_K = 60


def _completeness(paper: Paper) -> int:
    return sum(
        bool(value)
        for value in (
            paper.abstract,
            paper.doi,
            paper.arxiv_id,
            paper.venue,
            paper.authors,
            paper.urls,
        )
    )


def score_paper(paper: Paper, *, rrf_k: int = _RRF_K) -> float:
    """Fuse within-provider ranks without comparing raw provider scores."""

    score = 0.0
    for ranks in paper.source_ranks.values():
        for rank in set(ranks):
            score += 1.0 / (rrf_k + max(rank, 1))
    paper.fusion_score = score
    paper.source_count = len(paper.sources)
    return score


def rank_papers(papers: list[Paper]) -> list[Paper]:
    for paper in papers:
        score_paper(paper)

    # Reverse date ordering within a descending score/source grouping is easiest
    # with a separate stable pass, keeping the final order deterministic.
    ranked = sorted(papers, key=lambda paper: paper.title.casefold())
    ranked = sorted(ranked, key=lambda paper: _completeness(paper), reverse=True)
    ranked = sorted(ranked, key=lambda paper: paper.published_at or "0000-00-00", reverse=True)
    ranked = sorted(ranked, key=lambda paper: paper.source_count, reverse=True)
    ranked = sorted(ranked, key=lambda paper: paper.fusion_score, reverse=True)
    return ranked


def filter_by_date(papers: list[Paper], since: date, until: date) -> list[Paper]:
    """Apply the hard publication-date boundary before deduplication."""

    result: list[Paper] = []
    for paper in papers:
        if not paper.published_at:
            continue
        try:
            published = date.fromisoformat(paper.published_at)
        except ValueError:
            continue
        if since <= published <= until:
            result.append(paper)
    return result
