"""
Prompt Engineering Package
Explore zero-shot, few-shot, and chain-of-thought prompting techniques.
"""

__version__ = "0.1.0"
__author__ = "ExploreAI"

from .prompt_engineering import (
    call_llm,
    classify_zero_shot,
    classify_few_shot,
    classify_chain_of_thought,
)

__all__ = [
    "call_llm",
    "classify_zero_shot",
    "classify_few_shot",
    "classify_chain_of_thought",
]

