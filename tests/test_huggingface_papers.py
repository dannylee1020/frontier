from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.dedupe import deduplicate  # noqa: E402
from frontier_search.models import SearchRequest, SourceRecord  # noqa: E402
from frontier_search.sources.huggingface_papers import HuggingFacePapersAdapter  # noqa: E402


class HuggingFacePapersTests(unittest.TestCase):
    @patch("frontier_search.sources.huggingface_papers.request_json_value")
    def test_filters_global_feed_and_preserves_momentum_metadata(self, request_json_value) -> None:
        request_json_value.return_value = [
            {
                "paper": {
                    "id": "2602.00001v2",
                    "title": "Dynamic Reinforcement Learning",
                    "summary": "We study reinforcement learning for adaptive agents.",
                    "publishedAt": "2026-02-10T00:00:00Z",
                    "authors": [{"name": "Ada Lovelace"}],
                    "upvotes": 12,
                },
                "submittedOnDailyAt": "2026-02-12T00:00:00Z",
            },
            {
                "paper": {
                    "id": "2602.00002",
                    "title": "Unrelated Vision Benchmark",
                    "summary": "A benchmark for image recognition.",
                    "publishedAt": "2026-02-10T00:00:00Z",
                },
                "submittedOnDailyAt": "2026-02-12T00:00:00Z",
            },
        ]
        request = SearchRequest(
            ("reinforcement learning",), date(2026, 1, 1), date(2026, 3, 1)
        )

        response = HuggingFacePapersAdapter().search("reinforcement learning", request)

        self.assertEqual(response.role, "momentum")
        self.assertEqual(len(response.papers), 1)
        paper = response.papers[0]
        self.assertEqual(paper.arxiv_id, "2602.00001")
        self.assertEqual(paper.updated_at, "2026-02-12")
        self.assertEqual(paper.metadata["huggingface_rank"], 1)
        self.assertEqual(paper.metadata["huggingface_upvotes"], 12)

    @patch("frontier_search.sources.huggingface_papers.request_json_value")
    def test_reuses_one_feed_payload_across_query_branches(
        self, request_json_value
    ) -> None:
        request_json_value.return_value = []
        request = SearchRequest(
            ("robot learning", "embodied intelligence"),
            date(2026, 1, 1),
            date(2026, 3, 1),
        )
        adapter = HuggingFacePapersAdapter()

        adapter.search("robot learning", request)
        adapter.search("embodied intelligence", request)

        request_json_value.assert_called_once()

    @patch("frontier_search.sources.huggingface_papers.request_json_value")
    def test_merges_trending_paper_without_counting_it_as_scholarly_provider(
        self, request_json_value
    ) -> None:
        request_json_value.return_value = [
            {
                "paper": {
                    "id": "2602.00001",
                    "title": "Dynamic Reinforcement Learning",
                    "summary": "We study reinforcement learning for adaptive agents.",
                    "publishedAt": "2026-02-10",
                },
                "submittedOnDailyAt": "2026-02-12",
            }
        ]
        request = SearchRequest(
            ("reinforcement learning",), date(2026, 1, 1), date(2026, 3, 1)
        )
        trending = HuggingFacePapersAdapter().search(
            "reinforcement learning", request
        ).papers[0]
        scholarly = SourceRecord(
            source="arxiv",
            query="reinforcement learning",
            source_rank=1,
            title="Dynamic Reinforcement Learning",
            abstract="We study reinforcement learning for adaptive agents.",
            published_at="2026-02-10",
            arxiv_id="2602.00001v3",
        )

        papers = deduplicate([scholarly, trending])

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].sources, ["arxiv", "huggingface_papers"])
        self.assertEqual(papers[0].scholarly_sources, ["arxiv"])
        self.assertEqual(papers[0].momentum_sources, ["huggingface_papers"])
        self.assertEqual(papers[0].scholarly_source_count, 1)
        self.assertEqual(papers[0].metadata["momentum_signal"], "huggingface-trending-papers")


if __name__ == "__main__":
    unittest.main()
