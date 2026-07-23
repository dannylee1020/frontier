"""GitHub repository discovery adapter."""

from __future__ import annotations

import os
from urllib.parse import urlencode

from ..models import ArtifactRecord, ArtifactSearchResponse, SearchRequest
from ..transport import request_json
from .base import ArtifactSourceAdapter


_OFFICIAL_OWNERS = {
    "anthropics",
    "deepseek-ai",
    "google",
    "google-deepmind",
    "google-research",
    "huggingface",
    "meta-llama",
    "facebookresearch",
    "microsoft",
    "microsoftresearch",
    "moonshotai",
    "nvidia",
    "openai",
    "qwenlm",
    "zai-org",
    "thudm",
}


def _date_part(value: object) -> str | None:
    if not value:
        return None
    text = str(value)
    return text[:10] if len(text) >= 10 else None


def _authority(owner: str | None) -> str:
    if owner and owner.casefold() in _OFFICIAL_OWNERS:
        return "primary-official"
    return "community"


class GitHubAdapter(ArtifactSourceAdapter):
    name = "github"

    def search(self, query: str, request: SearchRequest) -> ArtifactSearchResponse:
        date_filter = f"created:{request.since.isoformat()}..{request.until.isoformat()}"
        search_query = f"{query} {date_filter}"
        params = urlencode(
            {
                "q": search_query,
                "sort": "updated",
                "order": "desc",
                "per_page": min(max(request.artifact_limit, 1), 100),
            }
        )
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        payload = request_json(
            f"https://api.github.com/search/repositories?{params}",
            headers=headers,
            timeout=request.timeout_seconds,
            max_retries=request.max_retries,
        )
        items = payload.get("items")
        if not isinstance(items, list):
            raise ValueError("GitHub response did not contain an items list")

        artifacts: list[ArtifactRecord] = []
        for index, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                continue
            full_name = str(item.get("full_name") or "").strip()
            url = str(item.get("html_url") or "").strip()
            if not full_name or not url:
                continue
            owner_data = item.get("owner")
            owner = (
                str(owner_data.get("login"))
                if isinstance(owner_data, dict) and owner_data.get("login")
                else full_name.split("/", 1)[0]
            )
            license_data = item.get("license")
            license_name = (
                str(license_data.get("spdx_id") or license_data.get("name"))
                if isinstance(license_data, dict)
                else None
            )
            artifacts.append(
                ArtifactRecord(
                    source=self.name,
                    query=query,
                    source_rank=index,
                    artifact_type="repository",
                    title=full_name,
                    description=(
                        str(item.get("description"))
                        if item.get("description")
                        else None
                    ),
                    url=url,
                    identifier=full_name,
                    owner=owner,
                    published_at=_date_part(item.get("created_at")),
                    updated_at=_date_part(item.get("updated_at")),
                    language=(
                        str(item.get("language"))
                        if item.get("language")
                        else None
                    ),
                    license=license_name,
                    tags=[str(topic) for topic in item.get("topics", []) if topic],
                    authority=_authority(owner),
                    metadata={
                        "full_name": full_name,
                        "default_branch": item.get("default_branch"),
                        "archived": item.get("archived", False),
                        "fork": item.get("fork", False),
                        "stars": item.get("stargazers_count"),
                        "open_issues": item.get("open_issues_count"),
                        "date_basis": "created_at",
                        "readme_url": url,
                    },
                )
            )
        return ArtifactSearchResponse(
            source=self.name,
            query=query,
            status="ok",
            artifacts=artifacts,
        )
