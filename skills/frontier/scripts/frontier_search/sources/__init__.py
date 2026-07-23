"""Research and artifact search provider adapters."""

from .arxiv import ArxivAdapter
from .base import ArtifactSourceAdapter, SourceAdapter
from .github import GitHubAdapter
from .huggingface import HuggingFaceAdapter
from .openalex import OpenAlexAdapter
from .semantic_scholar import SemanticScholarAdapter

__all__ = [
    "ArxivAdapter",
    "ArtifactSourceAdapter",
    "GitHubAdapter",
    "HuggingFaceAdapter",
    "OpenAlexAdapter",
    "SemanticScholarAdapter",
    "SourceAdapter",
]
