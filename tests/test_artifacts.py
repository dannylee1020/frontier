from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "frontier" / "scripts"))

from frontier_search.artifacts import deduplicate_artifacts, rank_artifacts  # noqa: E402
from frontier_search.models import ArtifactRecord, SearchRequest  # noqa: E402
from frontier_search.sources.github import GitHubAdapter  # noqa: E402
from frontier_search.sources.huggingface import HuggingFaceAdapter  # noqa: E402


class ArtifactTests(unittest.TestCase):
    def test_deduplicates_model_across_queries(self) -> None:
        records = [
            ArtifactRecord(
                source="huggingface",
                query="agent memory",
                source_rank=1,
                artifact_type="model",
                title="org/model",
                identifier="org/model",
                published_at="2026-02-01",
                authority="community",
            ),
            ArtifactRecord(
                source="huggingface",
                query="memory agent",
                source_rank=2,
                artifact_type="model",
                title="org/model",
                identifier="org/model",
                published_at="2026-02-01",
                authority="primary-official",
            ),
        ]
        artifacts = deduplicate_artifacts(records)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].matched_queries, ["agent memory", "memory agent"])
        self.assertEqual(artifacts[0].authority, "primary-official")
        self.assertEqual(rank_artifacts(artifacts)[0].title, "org/model")

    @patch("frontier_search.sources.huggingface.request_json_value")
    def test_huggingface_maps_model_card_metadata(self, request_json_value) -> None:
        request_json_value.return_value = [
            {
                "id": "Qwen/test-model",
                "createdAt": "2026-02-10T12:00:00Z",
                "lastModified": "2026-02-11T12:00:00Z",
                "pipeline_tag": "text-generation",
                "tags": ["agentic"],
                "license": "apache-2.0",
            }
        ]
        response = HuggingFaceAdapter().search(
            "agent", SearchRequest(("agent",), date(2026, 1, 1), date(2026, 3, 1))
        )
        self.assertEqual(response.artifacts[0].artifact_type, "model")
        self.assertEqual(response.artifacts[0].metadata["model_card_url"], "https://huggingface.co/Qwen/test-model")
        self.assertEqual(response.artifacts[0].authority, "primary-official")

    @patch("frontier_search.sources.github.request_json")
    def test_github_maps_repository_metadata(self, request_json) -> None:
        request_json.return_value = {
            "items": [
                {
                    "full_name": "openai/example-agent",
                    "html_url": "https://github.com/openai/example-agent",
                    "description": "A research harness",
                    "owner": {"login": "openai"},
                    "created_at": "2026-02-10T12:00:00Z",
                    "updated_at": "2026-02-11T12:00:00Z",
                    "language": "Python",
                    "topics": ["agents"],
                    "license": {"spdx_id": "MIT"},
                }
            ]
        }
        response = GitHubAdapter().search(
            "agent", SearchRequest(("agent",), date(2026, 1, 1), date(2026, 3, 1))
        )
        self.assertEqual(response.artifacts[0].artifact_type, "repository")
        self.assertEqual(response.artifacts[0].identifier, "openai/example-agent")
        self.assertEqual(response.artifacts[0].authority, "primary-official")


if __name__ == "__main__":
    unittest.main()
