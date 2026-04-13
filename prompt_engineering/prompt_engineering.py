"""
Prompt Engineering Explorer
Day 5–6: Zero-shot, few-shot, and chain-of-thought prompting techniques
         applied to customer support ticket classification.
"""

import os
import time
from typing import Optional

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
MODELS = {
    "haiku":  "claude-haiku-4-5",
    "sonnet": "claude-sonnet-4-5",
    "opus":   "claude-opus-4-5",
}

DEFAULT_MODEL = MODELS["haiku"]


# ---------------------------------------------------------------------------
# Client helper
# ---------------------------------------------------------------------------
def _get_client() -> Anthropic:
    """Return an authenticated Anthropic client."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Add it to .env.")
    return Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Core call (builds on Day 4 — simplified for prompt engineering focus)
# ---------------------------------------------------------------------------
def call_llm(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    max_tokens: int = 500,
) -> dict:
    """
    Call Claude and return the response + usage metadata.

    Temperature defaults to 0.0 for classification tasks (deterministic).

    Args:
        user_prompt:   The user message (the question / content to classify).
        system_prompt: Optional system-level instructions that guide Claude's
                       behaviour across the entire conversation.
        model:         Model identifier string.
        temperature:   Controls randomness (0.0 = deterministic).
        max_tokens:    Hard ceiling on output tokens.

    Returns:
        dict with keys: text, input_tokens, output_tokens, total_tokens,
                        model, latency_s
    """
    client = _get_client()

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    # system_prompt is a top-level parameter, NOT a message with role "system"
    if system_prompt:
        kwargs["system"] = system_prompt

    start = time.perf_counter()
    response = client.messages.create(**kwargs)
    latency = round(time.perf_counter() - start, 2)

    print('response:', response)
    return {
        "text": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "model": response.model,
        "latency_s": latency,
    }


# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE TICKETS  — used across all three prompting strategies
# ═══════════════════════════════════════════════════════════════════════════
SAMPLE_TICKETS = [
    "I've been charged twice for my subscription this month. Please refund the duplicate payment.",
    "How do I reset my password? I can't find the option in settings.",
    "Your product is terrible. Nothing works and I want to cancel everything immediately!",
    "Can you help me integrate your API with our existing CRM system?",
    "I'd like to upgrade my plan from Basic to Enterprise. What are the steps?",
]

# Categories the model should classify into
CATEGORIES = [
    "Billing",
    "Account Access",
    "Complaint",
    "Technical Support",
    "Sales / Upgrade",
]

# ---------------------------------------------------------------------------
# AMBIGUOUS TICKETS — designed to expose differences between strategies.
# Each ticket has overlapping signals from 2+ categories, making
# classification genuinely hard.  This is where strategies diverge.
# ---------------------------------------------------------------------------
AMBIGUOUS_TICKETS = [
    # Billing + Complaint overlap: is this a refund request or an angry complaint?
    "I'm furious! You charged me $200 for a plan I never signed up for. Fix this NOW or I'm calling my bank.",
    # Account Access + Technical Support overlap: is this a login issue or a bug?
    "Your SSO integration broke after the last update and now none of my team can log in.",
    # Sales + Complaint overlap: upgrading but threatening to leave
    "I want to upgrade, but honestly if the Enterprise plan doesn't fix these constant crashes I'm switching to a competitor.",
    # Billing + Sales overlap: asking about pricing while disputing a charge
    "Why was I charged $99? I thought the Pro plan was $49. Can you explain the pricing tiers?",
    # Technical Support + Account Access + Complaint: vague, multi-intent, emotional
    "nothing works. cant log in, api returns errors, and your docs are useless. im done.",
]


# ═══════════════════════════════════════════════════════════════════════════
# STRATEGY 1 — ZERO-SHOT PROMPTING
# ═══════════════════════════════════════════════════════════════════════════
#
# Zero-shot: Give the model a task with NO examples.
# The model relies entirely on its pre-trained knowledge.
# ═══════════════════════════════════════════════════════════════════════════

ZERO_SHOT_SYSTEM = """You are a customer support ticket classifier.

Classify each ticket into exactly ONE of these categories:
- Billing
- Account Access
- Complaint
- Technical Support
- Sales / Upgrade

Respond with ONLY the category name. No explanation."""


def classify_zero_shot(ticket: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Classify a support ticket using zero-shot prompting.

    Zero-shot means NO examples are provided — the model must rely on its
    pre-trained understanding of the task from the system prompt alone.

    Args:
        ticket: The customer support ticket text.
        model:  Model to use.

    Returns:
        dict with keys: ticket, category, input_tokens, output_tokens, latency_s
    """
    result = call_llm(
        user_prompt=f"Classify this ticket:\n\n{ticket}",
        system_prompt=ZERO_SHOT_SYSTEM,
        model=model,
    )

    print('result:', result)

    return {
        "ticket": ticket,
        "category": result["text"].strip(),
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "latency_s": result["latency_s"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# STRATEGY 2 — FEW-SHOT PROMPTING
# ═══════════════════════════════════════════════════════════════════════════
#
# Few-shot: Provide a handful of (input → output) examples so the model
# can learn the expected pattern and format from context.
# ═══════════════════════════════════════════════════════════════════════════

FEW_SHOT_SYSTEM = """You are a customer support ticket classifier.

Classify each ticket into exactly ONE of these categories:
- Billing
- Account Access
- Complaint
- Technical Support
- Sales / Upgrade

Here are some examples:

Ticket: "I was charged $49 but my plan is only $29."
Category: Billing

Ticket: "I can't log in, it says my account is locked."
Category: Account Access

Ticket: "This is the worst service I've ever used. I want a full refund now."
Category: Complaint

Now classify the next ticket. Respond with ONLY the category name."""


def classify_few_shot(ticket: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Classify a support ticket using few-shot prompting.

    Few-shot provides 3 labelled examples in the system prompt so the model
    sees the exact input/output pattern before handling a new ticket.
    This typically improves accuracy and format consistency vs. zero-shot.

    Args:
        ticket: The customer support ticket text.
        model:  Model to use.

    Returns:
        dict with keys: ticket, category, input_tokens, output_tokens, latency_s
    """
    result = call_llm(
        user_prompt=f"Ticket: \"{ticket}\"\nCategory:",
        system_prompt=FEW_SHOT_SYSTEM,
        model=model,
    )
    return {
        "ticket": ticket,
        "category": result["text"].strip(),
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "latency_s": result["latency_s"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# STRATEGY 3 — CHAIN-OF-THOUGHT PROMPTING
# ═══════════════════════════════════════════════════════════════════════════
#
# Chain-of-thought (CoT): Ask the model to reason step-by-step before
# giving its final answer.  This makes the model "think aloud" and
# typically improves accuracy on ambiguous or complex inputs.
# ═══════════════════════════════════════════════════════════════════════════

COT_SYSTEM = """You are a customer support ticket classifier.

Categories:
- Billing           → payments, charges, refunds, invoices
- Account Access    → login, password, account locked, settings
- Complaint         → frustration, anger, cancellation threats, negative feedback
- Technical Support → API, integration, bugs, technical how-to
- Sales / Upgrade   → plan changes, upgrades, pricing questions, new features

For each ticket, think step-by-step:
1. Identify the key words and customer intent.
2. Match the intent to the most relevant category.
3. State your final classification.

Respond in this exact format:
Reasoning: <your step-by-step reasoning>
Category: <one category from the list>"""


def classify_chain_of_thought(ticket: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Classify a support ticket using chain-of-thought prompting.

    CoT asks the model to reason step-by-step before classifying.
    This produces more accurate results on ambiguous tickets because the
    model "thinks aloud" instead of jumping to a conclusion.

    The trade-off: CoT uses more output tokens (and therefore costs more)
    because the model generates reasoning text in addition to the answer.

    Args:
        ticket: The customer support ticket text.
        model:  Model to use.

    Returns:
        dict with keys: ticket, reasoning, category, input_tokens, output_tokens, latency_s
    """
    result = call_llm(
        user_prompt=f"Classify this ticket:\n\n\"{ticket}\"",
        system_prompt=COT_SYSTEM,
        model=model,
    )

    # Parse the structured response
    text = result["text"].strip()
    reasoning = ""
    category = text

    if "Category:" in text:
        parts = text.split("Category:")
        reasoning_part = parts[0].strip()
        category = parts[-1].strip()
        # Remove "Reasoning:" prefix if present
        if reasoning_part.lower().startswith("reasoning:"):
            reasoning = reasoning_part[len("Reasoning:"):].strip()
        else:
            reasoning = reasoning_part

    return {
        "ticket": ticket,
        "reasoning": reasoning,
        "category": category,
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "latency_s": result["latency_s"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# TEST / DEMO FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def test_zero_shot() -> None:
    """Demonstrate zero-shot classification on all sample tickets."""
    print("\n" + "=" * 70)
    print("ZERO-SHOT PROMPTING")
    print("=" * 70)
    print("No examples provided — the model relies on its pre-trained knowledge.\n")
    print(f"📝 System prompt:\n   {ZERO_SHOT_SYSTEM[:100]}…\n")

    total_tokens = 0
    for i, ticket in enumerate(SAMPLE_TICKETS, 1):
        result = classify_zero_shot(ticket)
        total_tokens += result["input_tokens"] + result["output_tokens"]
        print(f"  {i}. [{result['category']:<20}]  {ticket[:65]}…")
        print(f"     ({result['input_tokens']} in / {result['output_tokens']} out / {result['latency_s']}s)")

    print(f"\n📊 Total tokens: {total_tokens}")
    print("\n💡 Zero-shot strengths:")
    print("   • Simplest prompt — no examples to write or maintain")
    print("   • Lowest input token count (cheapest)")
    print("   • Works well for straightforward tasks")
    print("\n💡 Zero-shot weaknesses:")
    print("   • Model may not match your exact category names")
    print("   • Output format can be inconsistent")
    print("   • Struggles with ambiguous or nuanced inputs")


def test_few_shot() -> None:
    """Demonstrate few-shot classification on all sample tickets."""
    print("\n" + "=" * 70)
    print("FEW-SHOT PROMPTING  (3 examples)")
    print("=" * 70)
    print("3 labelled examples teach the model the expected pattern.\n")
    print(f"📝 System prompt (with examples):\n   {FEW_SHOT_SYSTEM[:100]}…\n")

    total_tokens = 0
    for i, ticket in enumerate(SAMPLE_TICKETS, 1):
        result = classify_few_shot(ticket)
        total_tokens += result["input_tokens"] + result["output_tokens"]
        print(f"  {i}. [{result['category']:<20}]  {ticket[:65]}…")
        print(f"     ({result['input_tokens']} in / {result['output_tokens']} out / {result['latency_s']}s)")

    print(f"\n📊 Total tokens: {total_tokens}")
    print("\n💡 Few-shot strengths:")
    print("   • Examples anchor the model to your exact categories and format")
    print("   • Much more consistent output than zero-shot")
    print("   • Good balance between accuracy and token cost")
    print("\n💡 Few-shot weaknesses:")
    print("   • More input tokens (each example adds to every call)")
    print("   • Examples may bias the model toward similar inputs")
    print("   • You need to choose representative, diverse examples")


def test_chain_of_thought() -> None:
    """Demonstrate chain-of-thought classification on all sample tickets."""
    print("\n" + "=" * 70)
    print("CHAIN-OF-THOUGHT PROMPTING")
    print("=" * 70)
    print("The model reasons step-by-step before classifying.\n")
    print(f"📝 System prompt:\n   {COT_SYSTEM[:100]}…\n")

    total_tokens = 0
    for i, ticket in enumerate(SAMPLE_TICKETS, 1):
        result = classify_chain_of_thought(ticket)
        total_tokens += result["input_tokens"] + result["output_tokens"]
        print(f"  {i}. [{result['category']:<20}]  {ticket[:65]}…")
        print(f"     Reasoning: {result['reasoning'][:90]}…")
        print(f"     ({result['input_tokens']} in / {result['output_tokens']} out / {result['latency_s']}s)")
        print()

    print(f"📊 Total tokens: {total_tokens}")
    print("\n💡 CoT strengths:")
    print("   • Most accurate on ambiguous or multi-intent tickets")
    print("   • Reasoning is visible — you can debug wrong classifications")
    print("   • Model is less likely to make careless mistakes")
    print("\n💡 CoT weaknesses:")
    print("   • Highest output token count (most expensive)")
    print("   • Slower — more text to generate")
    print("   • Reasoning text needs to be parsed out of the response")


def test_comparison() -> None:
    """Run all three strategies on ambiguous tickets to expose differences."""
    print("\n" + "=" * 70)
    print("SIDE-BY-SIDE COMPARISON  (ambiguous tickets that expose differences)")
    print("=" * 70)
    print("\nOptions 1–3 used easy tickets where all strategies agree.")
    print("These tickets are deliberately ambiguous — they have signals")
    print("from 2+ categories, so the strategies may DISAGREE.\n")

    total_zs_tokens = 0
    total_fs_tokens = 0
    total_cot_tokens = 0
    disagreements = 0

    for i, ticket in enumerate(AMBIGUOUS_TICKETS, 1):
        print(f"{'─' * 70}")
        print(f"  Ticket {i}: \"{ticket[:80]}{'…' if len(ticket) > 80 else ''}\"")

        zs  = classify_zero_shot(ticket)
        fs  = classify_few_shot(ticket)
        cot = classify_chain_of_thought(ticket)

        total_zs_tokens  += zs["input_tokens"]  + zs["output_tokens"]
        total_fs_tokens  += fs["input_tokens"]  + fs["output_tokens"]
        total_cot_tokens += cot["input_tokens"] + cot["output_tokens"]

        # Check if all three agree
        all_same = (zs["category"] == fs["category"] == cot["category"])
        marker = "  ✅ All agree" if all_same else "  ⚡ DISAGREE"
        if not all_same:
            disagreements += 1

        print(f"    Zero-shot : {zs['category']:<22} ({zs['output_tokens']} out tokens)")
        print(f"    Few-shot  : {fs['category']:<22} ({fs['output_tokens']} out tokens)")
        print(f"    CoT       : {cot['category']:<22} ({cot['output_tokens']} out tokens)")
        if cot.get("reasoning"):
            print(f"    🧠 CoT reasoning: {cot['reasoning'][:100]}{'…' if len(cot.get('reasoning','')) > 100 else ''}")
        print(marker)
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n  Tickets tested    : {len(AMBIGUOUS_TICKETS)}")
    print(f"  Disagreements     : {disagreements} / {len(AMBIGUOUS_TICKETS)}")
    print(f"\n  {'Strategy':<22} {'Total tokens':>14}")
    print(f"  {'─'*22} {'─'*14}")
    print(f"  {'Zero-shot':<22} {total_zs_tokens:>14}")
    print(f"  {'Few-shot (3 examples)':<22} {total_fs_tokens:>14}")
    print(f"  {'Chain-of-thought':<22} {total_cot_tokens:>14}")

    print("\n💡 Why the strategies differ on ambiguous tickets:")
    print("   • Zero-shot has no guidance — it picks whichever category 'feels' right")
    print("   • Few-shot is anchored by examples, but the examples may not cover edge cases")
    print("   • CoT reasons through the ambiguity step-by-step, weighing competing signals")
    print("   • CoT uses the MOST tokens but is most likely to pick the 'correct' category")
    print("\n💡 This is the core trade-off:")
    print("   Easy tickets  → all strategies work, use zero-shot (cheapest)")
    print("   Hard tickets  → CoT is worth the extra cost for accuracy")


# ═══════════════════════════════════════════════════════════════════════════
# INTERACTIVE MENU
# ═══════════════════════════════════════════════════════════════════════════

def interactive_mode() -> None:
    print("\n" + "=" * 70)
    print("INTERACTIVE PROMPT ENGINEERING EXPLORER")
    print("=" * 70)

    while True:
        print("\nOptions:")
        print("1. Zero-Shot Prompting Demo")
        print("2. Few-Shot Prompting Demo  (3 examples)")
        print("3. Chain-of-Thought Prompting Demo")
        print("4. Side-by-Side Comparison  (ambiguous tickets — strategies DISAGREE)")
        print("5. Custom Ticket            (classify your own text)")
        print("6. Exit")

        choice = input("\nChoose an option (1-6): ").strip()

        if choice == "1":
            test_zero_shot()
        elif choice == "2":
            test_few_shot()
        elif choice == "3":
            test_chain_of_thought()
        elif choice == "4":
            test_comparison()
        elif choice == "5":
            ticket = input("Enter your support ticket: ").strip()
            if not ticket:
                print("No ticket entered.")
                continue
            strategy = input("Strategy [zero/few/cot] (default: cot): ").strip().lower() or "cot"
            print(f"\n📝 Ticket  : {ticket}")
            print(f"🔧 Strategy: {strategy}\n")
            try:
                if strategy == "zero":
                    result = classify_zero_shot(ticket)
                elif strategy == "few":
                    result = classify_few_shot(ticket)
                else:
                    result = classify_chain_of_thought(ticket)

                print(f"📁 Category: {result['category']}")
                if result.get("reasoning"):
                    print(f"🧠 Reasoning: {result['reasoning']}")
                print(
                    f"\n📊 Usage: {result['input_tokens']} in / "
                    f"{result['output_tokens']} out / {result['latency_s']}s"
                )
            except Exception as exc:
                print(f"Error: {exc}")
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def main() -> None:
    print("=" * 70)
    print("🎯 PROMPT ENGINEERING EXPLORER (Day 5)")
    print("=" * 70)
    print("Master zero-shot, few-shot, and chain-of-thought prompting!")
    print("Task: Classify customer support tickets into categories.")
    interactive_mode()


if __name__ == "__main__":
    main()

