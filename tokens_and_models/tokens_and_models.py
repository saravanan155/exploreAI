"""
Tokens & Models Explorer
Day 3: Understand token counting, model comparison, and how model choice impacts outputs.
"""

import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()


def get_client() -> Anthropic:
    """Return an authenticated Anthropic client."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Please add it to the .env file."
        )
    return Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Available models to compare (from smallest/fastest → most capable)
# ---------------------------------------------------------------------------
MODELS = {
    "haiku":  "claude-haiku-4-5",     # Fast & cheap
    "sonnet": "claude-sonnet-4-5",    # Balanced
    "opus":   "claude-opus-4-5",      # Most capable
}


def call_llm(
    question: str,
    model: str = "claude-sonnet-4-5",
    temperature: float = 0.7,
    max_tokens: int = 500,
) -> dict:
    """
    Call a Claude model and return the response together with usage metadata.

    Args:
        question:    The prompt to send.
        model:       Model identifier string.
        temperature: Controls randomness (0.0 – 1.0).
        max_tokens:  Maximum tokens to generate.

    Returns:
        dict with keys: text, input_tokens, output_tokens, model, latency_s
    """
    client = get_client()

    start = time.perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": question}],
    )
    latency = round(time.perf_counter() - start, 2)

    return {
        "text": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "model": response.model,
        "latency_s": latency,
    }


def count_tokens(text: str, model: str = "claude-sonnet-4-5") -> int:
    """
    Use the Anthropic token-counting endpoint to count tokens for a given text.

    Note: The count includes ~5-7 structural tokens added by the message payload
    (role header, turn delimiters, etc.) on top of the actual content tokens.
    This overhead is constant per message and becomes negligible for longer texts.

    Args:
        text:  The text to count tokens for.
        model: Model to use for tokenisation.

    Returns:
        Total token count including message structure overhead.
    """
    client = get_client()
    result = client.messages.count_tokens(
        model=model,
        messages=[{"role": "user", "content": text}],
    )
    return result.input_tokens


def compare_models(prompt: str, max_tokens: int = 300) -> list[dict]:
    """
    Send the same prompt to all three Claude tiers and collect results.

    Args:
        prompt:     The prompt to test.
        max_tokens: Maximum tokens to generate per model.

    Returns:
        List of result dicts (one per model).
    """
    results = []
    for label, model_id in MODELS.items():
        print(f"  ⏳ Querying {label} ({model_id})…", flush=True)
        try:
            result = call_llm(prompt, model=model_id, max_tokens=max_tokens)
            result["label"] = label
            results.append(result)
        except Exception as exc:
            results.append({
                "label": label,
                "model": model_id,
                "text": f"ERROR: {exc}",
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "latency_s": 0,
            })
    return results


# ---------------------------------------------------------------------------
# Interactive test functions
# ---------------------------------------------------------------------------

def test_token_counting():
    """Demonstrate the token-counting API and how text length relates to token count."""
    print("\n" + "=" * 60)
    print("TOKEN COUNTING")
    print("=" * 60)
    print("Tokens ≠ characters. This demo shows the relationship.\n")

    samples = [
        "Hello!",
        "The quick brown fox jumps over the lazy dog.",
        "Supercalifragilisticexpialidocious",
        "def fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        "A" * 500,
    ]

    print(f"{'Text (truncated)':<50} {'Chars':>6} {'Tokens':>7}")
    print("-" * 65)
    for sample in samples:
        try:
            tokens = count_tokens(sample)
            preview = (sample[:47] + "...") if len(sample) > 50 else sample
            print(f"{preview:<50} {len(sample):>6} {tokens:>7}")
        except Exception as exc:
            print(f"Error counting tokens: {exc}")

    print("\n💡 Key insights:")
    print("   • ~4 characters ≈ 1 token for English text.")
    print("   • Code, punctuation, and rare words can tokenise differently.")
    print()
    print("   ⚠️  Why does 'Hello!' (6 chars) show 9 tokens instead of ~2?")
    print("   The API counts tokens for the *entire message payload*, not just")
    print("   the raw text. Every message carries hidden structural tokens that")
    print("   Claude uses to understand the conversation format:")
    print()
    print("     Conversation start marker   → ~1 token")
    print("     Role header  ('user')       → ~2-3 tokens")
    print("     Content ('Hello!')          → ~2 tokens")
    print("     Message end marker          → ~1-2 tokens")
    print("     ─────────────────────────────────────────")
    print("     Total                       → ~9 tokens")
    print()
    print("   This fixed overhead is constant regardless of message length.")
    print("   For short texts it dominates; for longer texts it becomes negligible.")


def test_model_comparison():
    """Compare Haiku, Sonnet, and Opus on the same prompts."""
    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    print("Same prompt → Haiku (fast) | Sonnet (balanced) | Opus (powerful)\n")

    prompts = [
        {
            "prompt": "Explain what a neural network is in one sentence.",
            "description": "Factual / concise",
        },
        {
            "prompt": "Write a haiku about machine learning.",
            "description": "Creative",
        },
        {
            "prompt": (
                "A snail climbs 3 m up a wall during the day and slides back 2 m at night. "
                "How many days does it take to reach the top of a 10 m wall?"
            ),
            "description": "Reasoning / math",
        },
    ]

    for scenario in prompts:
        print(f"\n🎯 {scenario['description'].upper()}")
        print(f"Prompt: {scenario['prompt']}\n")

        results = compare_models(scenario["prompt"])

        print(
            f"\n{'Model':<10} {'In Tok':>7} {'Out Tok':>8} {'Total':>7} {'Latency':>9}  Response"
        )
        print("-" * 90)
        for r in results:
            preview = r["text"].replace("\n", " ")
            preview = (preview[:45] + "…") if len(preview) > 48 else preview
            print(
                f"{r['label']:<10} {r['input_tokens']:>7} {r['output_tokens']:>8} "
                f"{r['total_tokens']:>7} {r['latency_s']:>8}s  {preview}"
            )

        print()


def test_max_tokens_effect():
    """Show how max_tokens truncates responses and changes output quality."""
    print("\n" + "=" * 60)
    print("MAX_TOKENS EFFECT")
    print("=" * 60)
    prompt = "Explain the history of artificial intelligence in detail."
    print(f"Prompt: {prompt}\n")

    limits = [50, 150, 500]
    for limit in limits:
        print(f"🔢 max_tokens = {limit}")
        try:
            result = call_llm(prompt, max_tokens=limit)
            preview = result["text"][:200].replace("\n", " ")
            truncated = "…" if len(result["text"]) >= limit * 3 else ""
            print(f"   Output tokens used : {result['output_tokens']}")
            print(f"   Response           : {preview}{truncated}")
        except Exception as exc:
            print(f"   Error: {exc}")
        print("-" * 60)


def test_cost_estimation():
    """Estimate the API cost for different models and token counts."""
    print("\n" + "=" * 60)
    print("COST ESTIMATION (USD per 1 M tokens, approximate)")
    print("=" * 60)

    # Prices as of April 2026 (check https://www.anthropic.com/pricing)
    pricing = {
        "haiku":  {"input": 0.80,  "output": 4.00},
        "sonnet": {"input": 3.00,  "output": 15.00},
        "opus":   {"input": 15.00, "output": 75.00},
    }

    sample_workloads = [
        {"name": "10 k short Q&A pairs",  "input_tokens": 200,  "output_tokens": 100,  "calls": 10_000},
        {"name": "1 k document summaries", "input_tokens": 2_000, "output_tokens": 500,  "calls": 1_000},
        {"name": "100 long analyses",      "input_tokens": 8_000, "output_tokens": 2_000, "calls": 100},
    ]

    for workload in sample_workloads:
        print(f"\n📊 Workload: {workload['name']}")
        print(
            f"   {workload['calls']:,} calls × "
            f"{workload['input_tokens']:,} input tokens + "
            f"{workload['output_tokens']:,} output tokens"
        )
        print(f"   {'Model':<10} {'Input cost':>12} {'Output cost':>13} {'Total':>12}")
        print("   " + "-" * 50)
        for label, rates in pricing.items():
            total_in  = workload["calls"] * workload["input_tokens"]
            total_out = workload["calls"] * workload["output_tokens"]
            cost_in   = total_in  / 1_000_000 * rates["input"]
            cost_out  = total_out / 1_000_000 * rates["output"]
            print(
                f"   {label:<10} ${cost_in:>11.4f} ${cost_out:>12.4f} ${cost_in + cost_out:>11.4f}"
            )


def interactive_mode():
    """Interactive menu for token & model exploration."""
    print("\n" + "=" * 60)
    print("INTERACTIVE TOKENS & MODELS EXPLORER")
    print("=" * 60)

    while True:
        print("\nOptions:")
        print("1. Token Counting Demo")
        print("2. Model Comparison (Haiku / Sonnet / Opus)")
        print("3. max_tokens Effect")
        print("4. Cost Estimation")
        print("5. Custom Prompt")
        print("6. Exit")

        choice = input("\nChoose an option (1-6): ").strip()

        if choice == "1":
            test_token_counting()
        elif choice == "2":
            test_model_comparison()
        elif choice == "3":
            test_max_tokens_effect()
        elif choice == "4":
            test_cost_estimation()
        elif choice == "5":
            prompt = input("Enter your prompt: ").strip()
            model_choice = input(
                f"Model [haiku/sonnet/opus] (default: sonnet): "
            ).strip().lower() or "sonnet"
            model_id = MODELS.get(model_choice, MODELS["sonnet"])
            max_tok = int(input("Max tokens (default 500): ").strip() or "500")

            print(f"\n⏳ Querying {model_id}…")
            try:
                result = call_llm(prompt, model=model_id, max_tokens=max_tok)
                print(f"\nResponse:\n{result['text']}")
                print(
                    f"\n📊 Usage: {result['input_tokens']} in / "
                    f"{result['output_tokens']} out / "
                    f"{result['total_tokens']} total | {result['latency_s']}s"
                )
            except Exception as exc:
                print(f"Error: {exc}")
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    """Main entry point for Day 3 exploration."""
    print("=" * 60)
    print("🔢 TOKENS & MODELS EXPLORER (Day 3)")
    print("=" * 60)
    print("Understand token counting, model tiers, and cost trade-offs!")

    interactive_mode()


if __name__ == "__main__":
    main()

