from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.dedupe import deduplicate  # noqa: E402
from frontier_search.models import SourceRecord  # noqa: E402


class DedupeTests(unittest.TestCase):
    def test_merges_cross_source_duplicate_by_doi(self) -> None:
        records = [
            SourceRecord(
                source="openalex",
                query="frontier",
                source_rank=1,
                title="A Study of Frontier Models",
                authors=["Ada Lovelace"],
                abstract="Short abstract",
                published_at="2026-02-10",
                doi="10.1234/example.1",
            ),
            SourceRecord(
                source="semantic_scholar",
                query="frontier models",
                source_rank=2,
                title="A Study of Frontier Models",
                authors=["Ada Lovelace", "Grace Hopper"],
                abstract="A much longer and more complete abstract for this paper.",
                published_at="2026-02-10",
                doi="https://doi.org/10.1234/EXAMPLE.1",
                semantic_scholar_id="s2-1",
            ),
        ]
        papers = deduplicate(records)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].sources, ["openalex", "semantic_scholar"])
        self.assertEqual(papers[0].semantic_scholar_id, "s2-1")
        self.assertIn("much longer", papers[0].abstract or "")
        self.assertEqual(papers[0].source_count, 2)

    def test_title_match_requires_compatible_first_author(self) -> None:
        records = [
            SourceRecord(
                source="openalex",
                query="topic",
                source_rank=1,
                title="Same Title",
                authors=["First Author"],
                published_at="2026-01-01",
            ),
            SourceRecord(
                source="arxiv",
                query="topic",
                source_rank=1,
                title="Same Title",
                authors=["Different Author"],
                published_at="2026-01-01",
            ),
        ]
        self.assertEqual(len(deduplicate(records)), 2)


if __name__ == "__main__":
    unittest.main()
