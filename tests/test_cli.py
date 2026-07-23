from __future__ import annotations

import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.cli import main  # noqa: E402
from frontier_search.models import SearchRequest, SearchResponse, SourceRecord  # noqa: E402
from frontier_search.search import run_search  # noqa: E402


class FakeAdapter:
    def __init__(self, name: str, papers: list[SourceRecord], error: str | None = None):
        self.name = name
        self.papers = papers
        self.error = error

    def search(self, query: str, request: SearchRequest) -> SearchResponse:
        if self.error:
            raise RuntimeError(self.error)
        return SearchResponse(
            source=self.name,
            query=query,
            status="ok",
            papers=[
                SourceRecord(
                    source=record.source,
                    query=query,
                    source_rank=record.source_rank,
                    title=record.title,
                    authors=record.authors,
                    abstract=record.abstract,
                    published_at=record.published_at,
                    doi=record.doi,
                    arxiv_id=record.arxiv_id,
                    semantic_scholar_id=record.semantic_scholar_id,
                    venue=record.venue,
                )
                for record in self.papers
            ],
        )


class CliAndPipelineTests(unittest.TestCase):
    def test_pipeline_filters_old_records_and_survives_provider_failure(self) -> None:
        records = [
            SourceRecord(
                source="fake",
                query="frontier",
                source_rank=1,
                title="Recent result",
                authors=["Author"],
                abstract="An abstract.",
                published_at="2026-02-01",
                doi="10.1/recent",
            ),
            SourceRecord(
                source="fake",
                query="frontier",
                source_rank=2,
                title="Old result",
                published_at="2024-01-01",
            ),
        ]
        request = SearchRequest(
            queries=("frontier",),
            since=date(2026, 1, 1),
            until=date(2026, 3, 1),
        )
        run = run_search(
            request,
            adapters=[FakeAdapter("good", records), FakeAdapter("bad", [], "offline")],
            artifact_adapters=[],
        )
        self.assertEqual(run.counts["raw"], 2)  # two records from the good adapter/query
        self.assertEqual(run.counts["date_filtered"], 1)
        self.assertEqual(run.counts["deduplicated"], 1)
        self.assertEqual(run.papers[0].title, "Recent result")
        statuses = run.to_dict()["source_status"]
        self.assertEqual(statuses["bad"]["status"], "partial")

    def test_help_is_available(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            main(["--help"])
        self.assertEqual(raised.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
