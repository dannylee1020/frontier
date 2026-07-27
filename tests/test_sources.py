from __future__ import annotations

import json
import os
import sys
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.sources.arxiv import ArxivAdapter, _search_query  # noqa: E402
from frontier_search.sources.openalex import OpenAlexAdapter  # noqa: E402
from frontier_search.sources.semantic_scholar import SemanticScholarAdapter  # noqa: E402
from frontier_search.models import SearchRequest  # noqa: E402


class SourceParsingTests(unittest.TestCase):
    def test_openalex_parser_reconstructs_abstract_and_ids(self) -> None:
        payload = json.loads((ROOT / "tests/fixtures/openalex.json").read_text())
        papers = OpenAlexAdapter.parse_results(payload["results"], "frontier")
        self.assertEqual(len(papers), 2)
        self.assertEqual(papers[0].doi, "10.1234/example.1")
        self.assertEqual(papers[0].abstract, "We evaluate frontier models")
        self.assertEqual(papers[0].authors[0], "Ada Lovelace")

    def test_arxiv_parser_strips_version_from_identity(self) -> None:
        xml = (ROOT / "tests/fixtures/arxiv.xml").read_text()
        papers = ArxivAdapter.parse_results(xml, "frontier")
        self.assertEqual(len(papers), 2)
        self.assertEqual(papers[0].arxiv_id, "2602.00001")
        self.assertEqual(papers[0].doi, "10.1234/example.1")
        self.assertEqual(papers[0].publication_status, "preprint")

    def test_arxiv_query_uses_conjunctive_terms_not_one_exact_phrase(self) -> None:
        query = _search_query("physical AI training data")

        self.assertEqual(
            query,
            'all:"physical" AND all:"AI" AND all:"training" AND all:"data"',
        )
        self.assertNotIn('all:"physical AI training data"', query)

    def test_semantic_scholar_parser_handles_missing_abstract(self) -> None:
        payload = json.loads((ROOT / "tests/fixtures/semantic_scholar.json").read_text())
        papers = SemanticScholarAdapter.parse_results(payload["data"], "frontier")
        self.assertEqual(len(papers), 2)
        self.assertEqual(papers[0].semantic_scholar_id, "s2-1")
        self.assertIsNone(papers[1].abstract)
        self.assertEqual(papers[1].publication_status, "unknown")

    def test_semantic_scholar_serializes_query_branches(self) -> None:
        self.assertEqual(SemanticScholarAdapter.max_concurrency, 1)

    def test_semantic_scholar_requires_api_key(self) -> None:
        request = SearchRequest(
            queries=("frontier",),
            since=date(2026, 1, 1),
            until=date(2026, 2, 1),
        )

        with patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": "  "}):
            with self.assertRaisesRegex(
                RuntimeError,
                "SEMANTIC_SCHOLAR_API_KEY is required",
            ):
                SemanticScholarAdapter().search("frontier", request)

    @patch("frontier_search.sources.semantic_scholar.request_json")
    def test_semantic_scholar_sends_configured_api_key(self, request_json) -> None:
        request_json.return_value = {"data": []}
        request = SearchRequest(
            queries=("frontier",),
            since=date(2026, 1, 1),
            until=date(2026, 2, 1),
        )

        with patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": " test-key "}):
            SemanticScholarAdapter().search("frontier", request)

        self.assertEqual(
            request_json.call_args.kwargs["headers"],
            {"x-api-key": "test-key"},
        )


if __name__ == "__main__":
    unittest.main()
