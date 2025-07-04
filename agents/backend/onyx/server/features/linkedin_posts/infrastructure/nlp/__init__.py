"""
NLP Infrastructure Package
==========================

Provides a unified interface (`get_nlp_pipeline`) that returns the
configured fast NLP enhancer with grammar, SEO and performance boosts.
"""

from functools import lru_cache
from typing import Protocol

from .pipelines.fast_pipeline import FastPipeline

# Optional: here we could switch between different strategies (fast vs async)

class NLPPipeline(Protocol):
    async def enhance(self, text: str): ...


@lru_cache(maxsize=1)
def get_pipeline() -> NLPPipeline:
    """Return the default NLP pipeline (singleton)."""
    return FastPipeline() 