# basicllm - Basic Claude LLM Package

This is Stage 1 of the exploreAI project: A basic connection and question-answer implementation using Claude LLM.

## 🚀 Quick Start

```bash
cd basicllm
pip3 install -r requirements.txt
cp .env.example .env
# Add your Claude API key to .env (get from https://console.anthropic.com/)
python3 llm_basic.py
```

## 🔧 Setup Details

- **Python**: 3.9+
- **LLM**: Claude Sonnet 4.6 (via Anthropic API)
- **Dependencies**: `anthropic>=0.7.0`, `python-dotenv>=1.0.0`
- **Input**: Interactive - user enters their own questions

## 📦 Package Structure

```
basicllm/
├── __init__.py          # Package initialization (exports call_llm function)
├── llm_basic.py         # Main script with Claude connection and API calls
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── README.md            # This file
└── learnings            # Development notes and learnings
```

## 🎯 Features

- ✅ Simple Claude LLM connection using Anthropic API
- ✅ Interactive question input from user
- ✅ Secure API key management using environment variables
- ✅ Error handling and validation
- ✅ Modular code structure as a Python package

## 📋 Usage

Run the script and enter your question when prompted:

```bash
python3 llm_basic.py
# Enter your question: What is machine learning?
```

The script will display Claude's response formatted with separators.

## ⚠️ Limitations

- Knowledge cutoff: ~February 2026 (based on Claude Sonnet 4.6 training data)
- No real-time data access
- Cannot browse internet or access current APIs
- Responses based solely on training data

---

**Status:** ✅ Ready for use
**Last Updated:** April 6, 2026
