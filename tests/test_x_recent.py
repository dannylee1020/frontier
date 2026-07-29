from __future__ import annotations

import json
import os
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.models import SearchRequest, SearchResponse, SourceRecord, XPost, XSearchResponse  # noqa: E402
from frontier_search.sources.x_recent import (  # noqa: E402
    XRecentAdapter,
    _AccountRegistry,
    effective_window,
)
from frontier_search.x_query import build_x_query, x_query_budget  # noqa: E402
from frontier_search.x_trends import cluster_posts, deduplicate_posts  # noqa: E402
from frontier_search.search import run_search  # noqa: E402


class XRecentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads((ROOT / "tests/fixtures/x_recent.json").read_text())
        self.request = SearchRequest(
            ("long-horizon agents", "memory systems"),
            date(2026, 7, 1),
            date(2026, 7, 28),
            x_enabled=True,
            x_candidate_limit=20,
        )

    def test_query_is_broad_and_excludes_native_retweets_only(self) -> None:
        query = build_x_query('"memory augmented agents"')
        self.assertEqual(query, '"memory augmented agents" -is:retweet')
        self.assertNotIn("from:", query)
        self.assertEqual(x_query_budget(self.request.queries, 20, self.request.queries[0]), 10)
        self.assertEqual(x_query_budget(self.request.queries, 20, self.request.queries[1]), 10)

    def test_query_limit_is_explicit(self) -> None:
        with self.assertRaisesRegex(ValueError, "512-character"):
            build_x_query("x" * 510)

    def test_parser_preserves_authors_metrics_links_and_references(self) -> None:
        registry = _AccountRegistry(
            {
                "accounts": [
                    {
                        "organization": "Research Lab",
                        "usernames": ["ada_research"],
                        "account_type": "paper_author",
                    }
                ]
            }
        )
        posts = XRecentAdapter.parse_results(self.payload, "memory systems", registry)
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0].username, "ada_research")
        self.assertEqual(posts[0].author_class, "paper_author")
        self.assertEqual(posts[0].linked_urls, ["https://arxiv.org/abs/2607.00001"])
        self.assertEqual(posts[0].public_metrics["like_count"], 90)
        self.assertEqual(posts[1].referenced_posts[0]["type"], "replied_to")
        self.assertEqual(posts[0].url, "https://x.com/ada_research/status/1900000000000000001")

    @patch("frontier_search.sources.x_recent.effective_window")
    @patch("frontier_search.sources.x_recent.request_json")
    def test_search_uses_bearer_auth_window_pagination_and_budget(
        self, request_json, effective_window_mock
    ) -> None:
        effective_window_mock.return_value = (
            datetime(2026, 7, 28, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 7, 29, 0, 0, tzinfo=timezone.utc),
        )
        second_page = {
            "data": [self.payload["data"][0]],
            "includes": self.payload["includes"],
            "meta": {"result_count": 1},
        }
        request_json.side_effect = [
            {
                **self.payload,
                "meta": {"next_token": "next", "result_count": 2},
            },
            second_page,
        ]
        with patch.dict(os.environ, {"X_BEARER_TOKEN": "secret-token"}):
            response = XRecentAdapter().search("long-horizon agents", self.request)

        self.assertEqual(response.status, "ok")
        self.assertEqual(len(response.posts), 2)
        self.assertEqual(request_json.call_count, 2)
        first_url = request_json.call_args_list[0].args[0]
        params = parse_qs(urlsplit(first_url).query)
        self.assertEqual(params["max_results"], ["10"])
        self.assertEqual(params["start_time"], ["2026-07-28T00:00:00Z"])
        self.assertEqual(params["end_time"], ["2026-07-29T00:00:00Z"])
        self.assertNotIn("secret-token", first_url)
        self.assertEqual(
            request_json.call_args_list[0].kwargs["headers"]["Authorization"],
            "Bearer secret-token",
        )

    @patch("frontier_search.search.XRecentAdapter.is_configured", return_value=True)
    @patch("frontier_search.search.XRecentAdapter.search")
    def test_pipeline_keeps_x_out_of_paper_records(self, x_search, _configured) -> None:
        posts = XRecentAdapter.parse_results(self.payload, "long-horizon agents")
        x_search.side_effect = [
            XSearchResponse("x_recent", "long-horizon agents", "ok", posts=posts),
            XSearchResponse("x_recent", "memory systems", "ok", posts=posts),
        ]

        class EmptyPaperAdapter:
            name = "empty"
            role = "scholarly"

            def search(self, query: str, request: SearchRequest) -> SearchResponse:
                return SearchResponse("empty", query, "ok", papers=[])

        with patch.dict(os.environ, {"X_BEARER_TOKEN": "secret-token"}):
            run = run_search(
                self.request,
                adapters=[EmptyPaperAdapter()],
                momentum_adapters=[],
                on_progress=lambda _event: None,
            )

        artifact = run.to_dict()
        self.assertEqual(run.papers, [])
        self.assertEqual(run.counts["raw_x"], 4)
        self.assertEqual(run.counts["deduplicated_x"], 2)
        self.assertEqual(len(run.x_trends), 1)
        self.assertNotIn("x_recent", artifact["papers"])
        self.assertEqual(artifact["source_status"]["x_recent"]["role"], "social_momentum")
        self.assertEqual(artifact["source_status"]["x_recent"]["status"], "ok")

    def test_effective_window_intersects_recent_coverage(self) -> None:
        now = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)
        window = effective_window(self.request, now=now)
        self.assertEqual(window[0], datetime(2026, 7, 21, 12, 0, tzinfo=timezone.utc))
        self.assertEqual(window[1], datetime(2026, 7, 28, 11, 59, 30, tzinfo=timezone.utc))

    def test_posts_are_separate_from_papers_and_trends_cluster_locally(self) -> None:
        posts = XRecentAdapter.parse_results(self.payload, "memory systems")
        duplicate = XPost(**posts[0].__dict__)
        duplicate.post_id = "1900000000000000003"
        duplicate.edit_history_ids = [posts[0].post_id]
        self.assertEqual(len(deduplicate_posts([*posts, duplicate])), 2)
        trends = cluster_posts(posts)
        self.assertEqual(len(trends), 1)
        self.assertEqual(trends[0].post_count, 2)
        self.assertEqual(trends[0].unique_author_count, 2)
        self.assertEqual(trends[0].evidence_state, "artifact-linked")
        self.assertIn("visibility, not credibility", " ".join(trends[0].limitations))


if __name__ == "__main__":
    unittest.main()
