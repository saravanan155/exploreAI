# exploreAI

A step-by-step exploration of LLM capabilities, organized in self-contained stages.

## 📁 Stages

| Stage | Folder | Description | Status |
|-------|--------|-------------|--------|
| 1 | `basicllm/` | Basic Claude LLM connection and question-answer | ✅ Ready |
| 2 | `llm_with_rag/` | Retrieval Augmented Generation | 🔄 Coming Soon |
| 3 | - | Advanced Features | 📋 Planned |

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
└── [No README.md]       # Documentation centralized in root
```

Each stage is self-contained with its own dependencies and setup.
