"""Provider-independent ranking for merged paper candidates."""

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
    """Fuse scholarly-provider ranks without treating momentum as evidence."""

    score = 0.0
    for ranks in paper.source_ranks.values():
        if ranks:
            score += 1.0 / (rrf_k + max(min(ranks), 1))
    paper.fusion_score = score

    momentum_score = 0.0
    for ranks in paper.momentum_ranks.values():
        if ranks:
            momentum_score += 1.0 / (rrf_k + max(min(ranks), 1))
    paper.momentum_score = momentum_score
    paper.source_count = len(paper.sources)
    paper.scholarly_source_count = len(paper.scholarly_sources) or len(
        paper.source_ranks
    )
    return score


def rank_papers(papers: list[Paper]) -> list[Paper]:
    for paper in papers:
        score_paper(paper)

    # Momentum is deliberately a late tie-breaker. It can surface attention
    # among similarly supported papers, but cannot outrank scholarly evidence.
    ranked = sorted(papers, key=lambda paper: paper.title.casefold())
    ranked = sorted(ranked, key=lambda paper: _completeness(paper), reverse=True)
    ranked = sorted(ranked, key=lambda paper: paper.published_at or "0000-00-00", reverse=True)
    ranked = sorted(ranked, key=lambda paper: paper.momentum_score, reverse=True)
    ranked = sorted(
        ranked,
        key=lambda paper: len(
            {query.casefold() for query in paper.matched_queries if query}
        ),
        reverse=True,
    )
    ranked = sorted(ranked, key=lambda paper: paper.scholarly_source_count, reverse=True)
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
