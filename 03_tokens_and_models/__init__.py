"""
Tokens & Models Package
A package to explore token counting, model comparison, and parameter tuning.
"""

__version__ = "0.1.0"
__author__ = "ExploreAI"

from .tokens_and_models import call_llm, count_tokens, compare_models

__all__ = ["call_llm", "count_tokens", "compare_models"]

