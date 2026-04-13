# llm_intuition - LLM Intuition Explorer

This is Stage 2 (Day 2) of the exploreAI project: Exploring LLM behavior through temperature testing, context limits, and failure modes.

## 🚀 Quick Start

```bash
cd llm_intuition
pip3 install -r requirements.txt
cp .env.example .env
# Add your Claude API key to .env (get from https://console.anthropic.com/)
python3 llm_intuition.py
```

## 🔧 Setup Details

- **Python**: 3.9+
- **LLM**: Claude Sonnet 4.6 (via Anthropic API)
- **Dependencies**: `anthropic>=0.7.0`, `python-dotenv>=1.0.0`
- **Focus**: Temperature, context limits, failure modes

## 📦 Package Structure

```
llm_intuition/
├── __init__.py          # Package initialization (exports intuition functions)
├── llm_intuition.py     # Main script with intuition exploration features
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── README.md            # This file
└── learnings            # Development notes and learnings
```

## 🎯 Features

- ✅ **Enhanced Temperature Testing**: 4 carefully designed prompts showing clear creativity differences (0.0-1.0)
- ✅ **Context Limits**: Test how input length affects responses
- ✅ **Failure Modes**: Explore edge cases and LLM limitations
- ✅ **Top-p (Nucleus Sampling)**: Alternative to temperature for controlling diversity (0.0-1.0)
- ✅ **Top-k Sampling**: Limit vocabulary choices for more predictable outputs (10-50 tokens)
- ✅ **Stop Sequences**: Control response structure and length with custom termination strings
- ✅ **Interactive Mode**: Custom testing with configurable parameters
- ✅ **Secure API Management**: Environment variable-based authentication

## 📋 Usage

Run the script and choose from the interactive menu:

```bash
python3 llm_intuition.py
```

### Available Tests:
1. **Temperature Testing**: 4 optimized prompts demonstrating creativity differences
2. **Context Limits**: Test short vs. extremely long inputs
3. **Failure Modes**: Explore edge cases (empty input, vague questions, time-sensitive queries)
4. **Top-p Testing**: Nucleus sampling for controlling response diversity
5. **Top-k Testing**: Vocabulary limitation for predictability
6. **Stop Sequences**: Control response termination conditions
7. **Custom Questions**: Ask your own questions with custom parameters
8. **Exit**: Clean program termination

### Parameter Examples:
```python
# Temperature controls creativity
call_llm("Write a poem", temperature=0.0)  # Consistent
call_llm("Write a poem", temperature=1.0)  # Creative

# Top-p controls diversity (alternative to temperature)
call_llm("Describe a city", top_p=0.1)     # Focused
call_llm("Describe a city", top_p=0.9)     # Diverse

# Top-k limits vocabulary
call_llm("Medical advice:", top_k=20)      # Limited vocabulary

# Stop sequences control length
call_llm("List planets:", stop_sequences=["Earth"])  # Stop at Earth
```

## ⚠️ Limitations

- Knowledge cutoff: ~February 2026 (based on Claude Sonnet 4.6 training data)
- API rate limits may apply
- Context window limitations for very long inputs
- Temperature effects may vary between model versions

## 🎓 Learning Objectives

- Understand how **temperature** controls response creativity
- Learn about **context limits** and token constraints
- Explore **failure modes** and LLM limitations
- Practice **parameter tuning** for different use cases

---

**Status:** ✅ Ready for exploration
**Day:** 2 of 24
**Last Updated:** April 6, 2026
