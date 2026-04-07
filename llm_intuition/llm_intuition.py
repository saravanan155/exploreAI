"""
LLM Intuition Explorer
This script demonstrates LLM behavior with different temperatures, context limits, and failure modes.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

def call_llm(question: str, temperature: float = 0.7, max_tokens: int = 500,
            top_p: float = None, top_k: int = None, stop_sequences: list = None) -> str:
    """
    Call the Claude LLM model with configurable parameters.

    Args:
        question: The question to ask the LLM
        temperature: Controls randomness (0.0 = deterministic, 1.0 = very random)
        max_tokens: Maximum response length
        top_p: Nucleus sampling parameter (0.0-1.0, alternative to temperature)
        top_k: Top-k sampling parameter (limits vocabulary choices)
        stop_sequences: List of strings that stop generation when encountered

    Returns:
        The LLM's response as a string
    """
    # Initialize the Anthropic client with API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please add it to .env file.")

    client = Anthropic(api_key=api_key)

    # Build request parameters
    request_params = {
        "model": "claude-sonnet-4-6",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": question}]
    }

    # Add optional parameters if provided
    if temperature is not None:
        request_params["temperature"] = temperature
    if top_p is not None and temperature is None:
        request_params["top_p"] = top_p
    if top_k is not None:
        request_params["top_k"] = top_k
    if stop_sequences:
        request_params["stop_sequences"] = stop_sequences

    # Call the Claude LLM model
    response = client.messages.create(**request_params)

    # Extract and return the response text
    return response.content[0].text


def test_temperature():
    """Test how temperature affects response creativity with carefully chosen prompts."""

    # Carefully selected prompts that show clear temperature differences
    test_scenarios = [
        {
            "prompt": "Write a short poem about artificial intelligence",
            "description": "Creative writing - shows imagination differences"
        },
        {
            "prompt": "Invent a new ice cream flavor and describe it in detail",
            "description": "Creative invention - demonstrates originality"
        },
        {
            "prompt": "Give advice to someone learning to program for the first time",
            "description": "Advisory content - shows approach variations"
        },
        {
            "prompt": "Describe what life might be like on a planet where gravity is twice as strong as Earth",
            "description": "Speculative scenario - reveals creativity levels"
        }
    ]

    print("\n" + "="*60)
    print("TEMPERATURE TESTING WITH OPTIMIZED PROMPTS")
    print("="*60)
    print("Testing different temperatures: 0.0 (deterministic) → 0.5 (balanced) → 1.0 (creative)")
    print("Each prompt is designed to show clear differences between temperature levels.\n")

    temperatures = [0.0, 0.5, 1.0]

    for scenario in test_scenarios:
        print(f"\n🎯 {scenario['description'].upper()}")
        print(f"Prompt: {scenario['prompt']}\n")

        for temp in temperatures:
            print(f"🔥 Temperature: {temp}")
            try:
                response = call_llm(scenario['prompt'], temperature=temp, max_tokens=200)
                # Show first 150 chars to keep output manageable
                preview = response[:150] + "..." if len(response) > 150 else response
                print(f"Response: {preview}")
            except Exception as e:
                print(f"Error: {e}")
            print("-" * 50)

        print("\n" + "="*60)


def test_context_limits():
    """Test how context length affects responses."""
    print("\n" + "="*60)
    print("CONTEXT LIMITS TESTING")
    print("="*60)

    # Short context
    short_question = "What is AI?"
    print(f"Short context question: {short_question}")
    try:
        response = call_llm(short_question, max_tokens=50)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

    # Long context (trying to exceed limits)
    long_context = "A" * 10000 + " What does this text mean?"
    print(f"\nLong context ({len(long_context)} chars): {long_context[:50]}...")
    try:
        response = call_llm(long_context, max_tokens=100)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)


def test_failure_modes():
    """Test various failure modes and edge cases."""
    print("\n" + "="*60)
    print("FAILURE MODES TESTING")
    print("="*60)

    failure_tests = [
        "",  # Empty input
        "Write a story about absolutely nothing.",  # Vague/meaningless
        "Solve this equation: 2x + 3 = 7, where x = ?",  # Mathematical
        "What is the meaning of life, the universe, and everything?",  # Philosophical
        "Tell me something that happened yesterday in current events.",  # Time-sensitive
    ]

    for i, question in enumerate(failure_tests, 1):
        print(f"\nTest {i}: {question}")
        try:
            response = call_llm(question, temperature=0.3, max_tokens=150)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")


def test_top_p():
    """Test how top_p (nucleus sampling) affects response diversity."""
    question = "Describe a futuristic city in 3 sentences."

    print("\n" + "="*60)
    print("TOP-P (NUCLEUS SAMPLING) TESTING")
    print("="*60)
    print(f"Question: {question}")
    print("Top-p controls cumulative probability mass - lower = more focused, higher = more diverse\n")

    top_p_values = [0.1, 0.5, 0.9]

    for top_p in top_p_values:
        print(f"🎯 Top-p: {top_p}")
        try:
            response = call_llm(question, top_p=top_p, max_tokens=150)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)


def test_top_k():
    """Test how top_k affects vocabulary selection."""
    question = "Complete this sentence: The best programming language is"

    print("\n" + "="*60)
    print("TOP-K SAMPLING TESTING")
    print("="*60)
    print(f"Question: {question}")
    print("Top-k limits vocabulary to top k choices - lower = more predictable\n")

    top_k_values = [10, 50, None]  # None = no limit

    for top_k in top_k_values:
        label = top_k if top_k else "unlimited"
        print(f"🎯 Top-k: {label}")
        try:
            response = call_llm(question, top_k=top_k, max_tokens=100)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)


def test_stop_sequences():
    """Test how stop sequences control response length and structure."""
    question = "List the planets in our solar system:"

    print("\n" + "="*60)
    print("STOP SEQUENCES TESTING")
    print("="*60)
    print(f"Question: {question}")
    print("Stop sequences halt generation when encountered\n")

    # Test different stop conditions
    stop_tests = [
        {"stops": ["\n"], "desc": "Stop at first newline"},
        {"stops": ["Earth"], "desc": "Stop when 'Earth' is mentioned"},
        {"stops": ["Mars", "Jupiter"], "desc": "Stop at Mars OR Jupiter"},
        {"stops": None, "desc": "No stop sequences (normal)"}
    ]

    for test in stop_tests:
        print(f"🎯 {test['desc']}")
        try:
            response = call_llm(question, stop_sequences=test['stops'], max_tokens=200)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)


def interactive_mode():
    """Interactive mode for custom testing."""
    print("\n" + "="*60)
    print("INTERACTIVE LLM INTUITION EXPLORER")
    print("="*60)

    while True:
        print("\nOptions:")
        print("1. Test Temperature")
        print("2. Test Context Limits")
        print("3. Test Failure Modes")
        print("4. Test Top-p (Nucleus Sampling)")
        print("5. Test Top-k Sampling")
        print("6. Test Stop Sequences")
        print("7. Ask Custom Question")
        print("8. Exit")

        choice = input("\nChoose an option (1-8): ").strip()

        if choice == "1":
            test_temperature()
        elif choice == "2":
            test_context_limits()
        elif choice == "3":
            test_failure_modes()
        elif choice == "4":
            test_top_p()
        elif choice == "5":
            test_top_k()
        elif choice == "6":
            test_stop_sequences()
        elif choice == "7":
            question = input("Enter your question: ")
            temp = float(input("Temperature (0.0-1.0, default 0.7): ") or "0.7")
            max_tok = int(input("Max tokens (default 500): ") or "500")

            try:
                response = call_llm(question, temperature=temp, max_tokens=max_tok)
                print(f"\nResponse: {response}")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    """Main function for LLM intuition exploration."""
    print("=" * 60)
    print("🤖 LLM INTUITION EXPLORER (Day 2)")
    print("=" * 60)
    print("Explore temperature, context limits, and failure modes!")

    interactive_mode()


if __name__ == "__main__":
    main()
