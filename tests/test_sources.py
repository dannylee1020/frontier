from __future__ import annotations

import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.sources.arxiv import ArxivAdapter  # noqa: E402
from frontier_search.sources.openalex import OpenAlexAdapter  # noqa: E402
from frontier_search.sources.semantic_scholar import SemanticScholarAdapter  # noqa: E402


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

    def test_semantic_scholar_parser_handles_missing_abstract(self) -> None:
        payload = json.loads((ROOT / "tests/fixtures/semantic_scholar.json").read_text())
        papers = SemanticScholarAdapter.parse_results(payload["data"], "frontier")
        self.assertEqual(len(papers), 2)
        self.assertEqual(papers[0].semantic_scholar_id, "s2-1")
        self.assertIsNone(papers[1].abstract)
        self.assertEqual(papers[1].publication_status, "unknown")


if __name__ == "__main__":
    unittest.main()
