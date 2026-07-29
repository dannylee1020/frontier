"""Scholarly and research-attention paper provider adapters."""

from .arxiv import ArxivAdapter
from .base import SourceAdapter
from .huggingface_papers import HuggingFacePapersAdapter
from .openalex import OpenAlexAdapter
from .semantic_scholar import SemanticScholarAdapter
from .x_recent import XRecentAdapter

__all__ = [
    "ArxivAdapter",
    "HuggingFacePapersAdapter",
    "OpenAlexAdapter",
    "SemanticScholarAdapter",
    "SourceAdapter",
    "XRecentAdapter",
]
