"""Initialize prompts package."""

from .benchmark_prompts import (
    get_all_prompts,
    get_prompts_by_category,
    CODING_PROMPTS,
    SUMMARIZATION_PROMPTS,
    CREATIVE_WRITING_PROMPTS
)

__all__ = [
    "get_all_prompts",
    "get_prompts_by_category",
    "CODING_PROMPTS",
    "SUMMARIZATION_PROMPTS",
    "CREATIVE_WRITING_PROMPTS"
]
