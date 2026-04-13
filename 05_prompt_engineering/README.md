# prompt_engineering – Prompt Engineering Explorer

Day 5–6 of the exploreAI project: master prompting strategies — zero-shot, few-shot, and chain-of-thought — applied to customer support ticket classification.

## 🚀 Quick Start

```bash
cd prompt_engineering
cp .env.example .env
# Add your Claude API key to .env
pip3 install -r requirements.txt
python3 prompt_engineering.py
```

## 🔧 Setup Details

- **Python**: 3.9+
- **LLM**: Claude Haiku 4.5 (default) · Sonnet 4.5 · Opus 4.5
- **Dependencies**: `anthropic>=0.7.0`, `python-dotenv>=1.0.0`
- **Focus**: Prompting strategies for classification tasks

## 📦 Package Structure

```
prompt_engineering/
├── __init__.py                 # Package exports
├── prompt_engineering.py       # Main script
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── README.md                   # This file
└── LEARNINGS.md                # Development notes and learnings
```

## 🎯 Features

- ✅ **Zero-Shot Prompting**: Classify tickets with no examples — model uses pre-trained knowledge
- ✅ **Few-Shot Prompting**: 3 labelled examples teach the model the expected pattern and format
- ✅ **Chain-of-Thought Prompting**: Step-by-step reasoning before classification
- ✅ **Side-by-Side Comparison**: All 3 strategies on the same ticket — compare accuracy, tokens, latency
- ✅ **Custom Ticket Mode**: Classify your own text with any strategy
- ✅ **System Prompts**: Separate `system` parameter for role/behaviour instructions

## 📋 Usage

```bash
python3 prompt_engineering.py
```

### Menu Options:
1. **Zero-Shot Prompting Demo** – classify 5 tickets with no examples
2. **Few-Shot Prompting Demo** – classify 5 tickets with 3 labelled examples
3. **Chain-of-Thought Demo** – classify 5 tickets with step-by-step reasoning
4. **Side-by-Side Comparison** – all 3 strategies on one ticket
5. **Custom Ticket** – enter your own text, pick a strategy
6. **Exit**

### API Examples:

```python
from prompt_engineering import (
    classify_zero_shot,
    classify_few_shot,
    classify_chain_of_thought,
)

ticket = "I was charged twice for my subscription."

# Zero-shot — no examples
result = classify_zero_shot(ticket)
print(result["category"])   # "Billing"

# Few-shot — 3 examples in system prompt
result = classify_few_shot(ticket)
print(result["category"])   # "Billing"

# Chain-of-thought — reasoning + category
result = classify_chain_of_thought(ticket)
print(result["category"])   # "Billing"
print(result["reasoning"])  # "The customer mentions being charged twice…"
```

## 🎓 Prompting Strategy Comparison

| Strategy | Examples | Output | Tokens | Accuracy | Best For |
|---|---|---|---|---|---|
| **Zero-shot** | None | Category only | Lowest | Good | Simple, clear-cut tasks |
| **Few-shot** | 3 in system prompt | Category only | Medium | Better | Consistent format needed |
| **Chain-of-thought** | None (structured reasoning) | Reasoning + category | Highest | Best | Ambiguous or complex inputs |

## 📝 Classification Categories

| Category | Signals |
|---|---|
| Billing | Charges, refunds, payments, invoices |
| Account Access | Login, password, account locked, settings |
| Complaint | Frustration, anger, cancellation threats |
| Technical Support | API, integration, bugs, technical questions |
| Sales / Upgrade | Plan changes, upgrades, pricing questions |

## ⚠️ Limitations

- Temperature set to 0.0 for deterministic classification — raise for creative tasks
- Few-shot examples are hardcoded — production systems should load from a config file
- CoT parsing is simple string splitting — production should use structured outputs (Day 6)

## 🎓 Learning Objectives

- Understand the difference between zero-shot, few-shot, and chain-of-thought prompting
- Learn how system prompts differ from user messages in the Claude API
- Compare token cost vs. accuracy trade-offs across strategies
- Parse structured responses (reasoning + category) from CoT output

---

**Status:** 🚧 In Progress
**Day:** 5 of 30
**Last Updated:** April 12, 2026

