"""
LLM Intuition Package
A package to explore and understand LLM behavior with temperature, context limits, and failure modes.
"""

__version__ = "0.1.0"
__author__ = "ExploreAI"

from .llm_intuition import call_llm, test_temperature, test_context_limits, test_failure_modes, test_top_p, test_top_k, test_stop_sequences

__all__ = ["call_llm", "test_temperature", "test_context_limits", "test_failure_modes", "test_top_p", "test_top_k", "test_stop_sequences"]
