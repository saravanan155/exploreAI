# tokens_and_models – Tokens & Models Explorer

Day 3 of the exploreAI project: understand token counting, model tiers, and cost trade-offs when working with Claude.

## 🚀 Quick Start

```bash
cd tokens_and_models
cp .env.example .env
# Add your Claude API key to .env
python3 tokens_and_models.py
```

## 🔧 Setup Details

- **Python**: 3.9+
- **LLMs**: Claude Haiku 4.5 · Sonnet 4.5 · Opus 4.5 (via Anthropic API)
- **Dependencies**: `anthropic>=0.7.0`, `python-dotenv>=1.0.0`
- **Focus**: Token counting, model comparison, cost estimation

## 📦 Package Structure

```
tokens_and_models/
├── __init__.py              # Package initialization (exports call_llm, count_tokens, compare_models)
├── tokens_and_models.py     # Main script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── README.md                # This file
└── LEARNINGS.md             # Development notes and learnings
```

## 🎯 Features

- ✅ **Token Counting**: Use the Anthropic `count_tokens` API to count tokens before sending
- ✅ **Model Comparison**: Send the same prompt to Haiku, Sonnet, and Opus; compare quality, speed, and token usage
- ✅ **max_tokens Effect**: See how limiting output tokens truncates responses
- ✅ **Cost Estimation**: Calculate approximate API costs for different workloads
- ✅ **Interactive Mode**: Custom prompt testing with model and parameter selection

## 📋 Usage

```bash
python3 tokens_and_models.py
```

### Menu Options:
1. **Token Counting Demo** – character vs. token comparison for various text types
2. **Model Comparison** – Haiku / Sonnet / Opus side-by-side on factual, creative, and reasoning prompts
3. **max_tokens Effect** – watch responses get truncated at 50 / 150 / 500 tokens
4. **Cost Estimation** – USD cost projections for common workload sizes
5. **Custom Prompt** – your own prompt with model and token control
6. **Exit**

### API Examples:
```python
from tokens_and_models import call_llm, count_tokens, compare_models

# Count tokens before sending
n = count_tokens("Hello, how are you?")

# Call a specific model tier
result = call_llm("Explain RAG in one sentence.", model="claude-haiku-4-5")
print(result["text"], result["total_tokens"], result["latency_s"])

# Compare all three tiers
results = compare_models("Write a haiku about AI.")
```

## ⚠️ Limitations

- Opus is significantly more expensive – use selectively
- Token counts vary by model's tokeniser
- Pricing information may change – verify at https://www.anthropic.com/pricing

## 🎓 Learning Objectives

- Understand what **tokens** are and how they differ from characters
- Learn when to choose **Haiku vs. Sonnet vs. Opus**
- Estimate **API costs** before running at scale
- Practice interpreting **usage metadata** from the API response

---

**Status:** ✅ Complete  
**Day:** 3 of 24  
**Last Updated:** April 7, 2026

