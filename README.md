# exploreAI

A 24-day structured learning journey exploring LLM capabilities, organized in self-contained stages. Each stage builds on the previous, from basic API calls to full-stack applications with RAG, agents, and fine-tuning.

## 📁 Learning Stages

| Day | Stage | Folder | Description | Status |
|-----|-------|--------|-------------|--------|
| 1 | [`basicllm/`](basicllm/README.md) | Basic Claude LLM connection and question-answer | ✅ Complete |
| 2 | [`llm_intuition/`](llm_intuition/README.md) | Temperature testing, context limits, failure modes | ✅ Ready |
| 3 | `tokens_and_models/` | Token counting, model comparison, parameters | 📋 Planned |
| 4 | `reliable_api_calls/` | Retry logic, timeouts, structured logging | 📋 Planned |
| 5-6 | `prompt_engineering/` | JSON outputs, input validation, versioned prompts | 📋 Planned |
| 7-8 | `chatbot_backend/` | FastAPI endpoint, multi-turn conversations | 📋 Planned |
| 9-10 | `chatbot_frontend/` | React UI, streaming responses | 📋 Planned |
| 11-13 | `llm_with_rag/` | Document loading, chunking, semantic search | 📋 Planned |
| 14-15 | `tool_calling/` | Function calling, tool result handling | 📋 Planned |
| 16-17 | `agents/` | ReAct loops, multi-step reasoning | 📋 Planned |
| 18-19 | `evals_and_observability/` | Logging, test cases, LangSmith tracing | 📋 Planned |
| 20 | `cost_optimization/` | Caching, model routing, cost tracking | 📋 Planned |
| 21-23 | `fullstack_app/` | Complete application with all features | 📋 Planned |
| 24+ | `fine_tuning/` | Custom model training and evaluation | 📋 Planned |

## 🚀 Current Stage: LLM Intuition (Day 2)

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
- **Input**: Interactive - user enters their own questions

## 🧠 Key Learnings from Development

### API Evolution & Model Names
LLM APIs evolve rapidly - model names change frequently. Always verify available models via API calls using `client.models.list()`.

### Package Structure Importance
`__init__.py` transforms folders into importable packages, enabling `import basicllm` and `from basicllm import call_llm`.

### Environment Variable Management
`python-dotenv` simplifies `.env` file loading. Never hardcode API keys - use `load_dotenv()` + `os.getenv("API_KEY")`.

### Interactive Input Handling
`input()` function enables user interaction. Clear prompts improve user experience.

### API Error Handling
404 errors often mean invalid model names. Check API documentation and available models for debugging.

### Knowledge Cutoff Awareness
LLMs have training data cutoffs (~February 2026 for Claude Sonnet 4.6). No access to data after training period.

### Dependency Management
Use `requirements.txt` for reproducible environments. Specify minimum versions and use platform-appropriate commands (`pip3` on macOS).

## 📦 Package Structure

```
basicllm/                 # Day 1: Basic LLM connection
├── __init__.py          # Package initialization (exports call_llm function)
├── llm_basic.py         # Main script with Claude connection and API calls
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── README.md            # Folder-specific documentation
└── learnings            # Development notes and learnings

llm_intuition/           # Day 2: LLM intuition exploration
├── __init__.py          # Package initialization (exports intuition functions)
├── llm_intuition.py     # Main script with temperature/context/failure testing
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── README.md            # Folder-specific documentation
└── LEARNINGS.md         # Development notes and learnings
```

Each stage is self-contained with its own dependencies and setup.
