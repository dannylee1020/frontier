from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.models import Paper  # noqa: E402
from frontier_search.rank import rank_papers, score_paper  # noqa: E402


class RankTests(unittest.TestCase):
    def test_multi_source_appearance_is_strong_signal(self) -> None:
        shared = Paper(
            title="Shared",
            published_at="2026-01-01",
            sources=["openalex", "arxiv"],
            source_ranks={"openalex": [5], "arxiv": [5]},
        )
        single = Paper(
            title="Single",
            published_at="2026-02-01",
            sources=["semantic_scholar"],
            source_ranks={"semantic_scholar": [1]},
        )
        ranked = rank_papers([single, shared])
        self.assertEqual(ranked[0].title, "Shared")
        self.assertGreater(ranked[0].fusion_score, ranked[1].fusion_score)

    def test_ranking_is_deterministic_for_equal_inputs(self) -> None:
        papers = [
            Paper(title="B", published_at="2026-01-01", sources=["openalex"], source_ranks={"openalex": [1]}),
            Paper(title="A", published_at="2026-01-01", sources=["openalex"], source_ranks={"openalex": [1]}),
        ]
        self.assertEqual([p.title for p in rank_papers(papers)], ["A", "B"])

    def test_repeated_queries_from_one_provider_do_not_inflate_fusion(self) -> None:
        repeated = Paper(
            title="Repeated",
            source_ranks={"openalex": [1, 2, 3]},
        )
        single = Paper(
            title="Single",
            source_ranks={"openalex": [1]},
        )

        self.assertEqual(score_paper(repeated), score_paper(single))

    def test_cross_branch_coverage_is_a_late_relevance_tiebreaker(self) -> None:
        broad = Paper(
            title="Broad",
            published_at="2026-01-01",
            sources=["openalex"],
            source_ranks={"openalex": [1]},
            matched_queries=["robot learning", "embodied intelligence"],
        )
        narrow = Paper(
            title="Narrow",
            published_at="2026-01-01",
            sources=["openalex"],
            source_ranks={"openalex": [1]},
            matched_queries=["robot learning"],
        )

        self.assertEqual(rank_papers([narrow, broad])[0].title, "Broad")


if __name__ == "__main__":
    unittest.main()
