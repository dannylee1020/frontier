"""Hugging Face model and model-card discovery adapter."""

from __future__ import annotations

from urllib.parse import urlencode

from ..models import ArtifactRecord, ArtifactSearchResponse, SearchRequest
from ..transport import request_json_value
from .base import ArtifactSourceAdapter


# Namespaces that commonly publish first-party frontier models. This is an
# authority signal only; downloads and likes are intentionally not ranking
# inputs.
_OFFICIAL_NAMESPACES = {
    "ai21labs",
    "allenai",
    "anthropic",
    "deepseek-ai",
    "google",
    "google-bert",
    "google-research",
    "meta-llama",
    "microsoft",
    "mistralai",
    "moonshotai",
    "nvidia",
    "openai",
    "qwen",
    "qwenlm",
    "zai-org",
}


def _date_part(value: object) -> str | None:
    if not value:
        return None
    text = str(value)
    return text[:10] if len(text) >= 10 else None


def _authority(owner: str | None) -> str:
    if owner and owner.casefold() in _OFFICIAL_NAMESPACES:
        return "primary-official"
    return "community"


class HuggingFaceAdapter(ArtifactSourceAdapter):
    name = "huggingface"

    def search(self, query: str, request: SearchRequest) -> ArtifactSearchResponse:
        params = urlencode(
            {
                "search": query,
                "sort": "createdAt",
                "direction": "-1",
                "limit": min(max(request.artifact_limit, 1), 100),
            }
        )
        payload = request_json_value(
            f"https://huggingface.co/api/models?{params}",
            headers={"Accept": "application/json"},
            timeout=request.timeout_seconds,
            max_retries=request.max_retries,
        )
        if not isinstance(payload, list):
            raise ValueError("Hugging Face response did not contain a model list")

        artifacts: list[ArtifactRecord] = []
        for index, item in enumerate(payload, start=1):
            if not isinstance(item, dict):
                continue
            model_id = str(item.get("modelId") or item.get("id") or "").strip()
            if not model_id:
                continue
            owner = model_id.split("/", 1)[0] if "/" in model_id else None
            created_at = _date_part(item.get("createdAt"))
            updated_at = _date_part(item.get("lastModified"))
            card_data = item.get("cardData")
            artifacts.append(
                ArtifactRecord(
                    source=self.name,
                    query=query,
                    source_rank=index,
                    artifact_type="model",
                    title=model_id,
                    description=(
                        str(item.get("pipeline_tag"))
                        if item.get("pipeline_tag")
                        else None
                    ),
                    url=f"https://huggingface.co/{model_id}",
                    identifier=model_id,
                    owner=owner,
                    published_at=created_at or updated_at,
                    updated_at=updated_at,
                    language=None,
                    license=(
                        str(item.get("license"))
                        if item.get("license")
                        else None
                    ),
                    tags=[str(tag) for tag in item.get("tags", []) if tag],
                    authority=_authority(owner),
                    metadata={
                        "model_id": model_id,
                        "model_card_url": f"https://huggingface.co/{model_id}",
                        "card_data_available": isinstance(card_data, dict),
                        "pipeline_tag": item.get("pipeline_tag"),
                        "library_name": item.get("library_name"),
                        "downloads": item.get("downloads"),
                        "likes": item.get("likes"),
                        "date_basis": "created_at" if created_at else "updated_at",
                    },
                )
            )
        return ArtifactSearchResponse(
            source=self.name,
            query=query,
            status="ok",
            artifacts=artifacts,
        )
