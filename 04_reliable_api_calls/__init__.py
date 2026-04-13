"""
Reliable API Calls Package
Production-ready LLM calls with retry logic, timeouts, structured logging,
jitter, request correlation IDs, cost calculation, and log rotation.
"""

__version__ = "0.1.0"
__author__ = "ExploreAI"

from .reliable_api_calls import (
    call_llm,
    call_llm_with_retry,
    call_llm_with_timeout,
    call_llm_logged,
    call_llm_reliable,
    calculate_cost,
    setup_logger,
)

__all__ = [
    "call_llm",
    "call_llm_with_retry",
    "call_llm_with_timeout",
    "call_llm_logged",
    "call_llm_reliable",
    "calculate_cost",
    "setup_logger",
]

