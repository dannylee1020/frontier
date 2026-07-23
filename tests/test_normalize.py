from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.normalize import (  # noqa: E402
    abstract_from_inverted_index,
    normalize_arxiv_id,
    normalize_date,
    normalize_doi,
    normalize_title,
)


class NormalizeTests(unittest.TestCase):
    def test_doi_normalization(self) -> None:
        self.assertEqual(normalize_doi("https://doi.org/10.1234/ABC."), "10.1234/abc")
        self.assertEqual(normalize_doi("doi:10.1234/ABC"), "10.1234/abc")

    def test_arxiv_normalization(self) -> None:
        self.assertEqual(normalize_arxiv_id("https://arxiv.org/abs/2602.00001v4"), "2602.00001")

    def test_title_normalization(self) -> None:
        self.assertEqual(normalize_title("A Study: of FRONTIER—Models!"), "a study of frontier models")

    def test_date_normalization(self) -> None:
        self.assertEqual(normalize_date("2026-02-10T10:00:00Z"), "2026-02-10")
        self.assertEqual(normalize_date(2026), "2026-01-01")

    def test_inverted_index(self) -> None:
        self.assertEqual(
            abstract_from_inverted_index({"models": [1], "Frontier": [0]}),
            "Frontier models",
        )


if __name__ == "__main__":
    unittest.main()
