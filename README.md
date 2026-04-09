# exploreAI

A structured learning journey exploring LLM capabilities end-to-end, organised in self-contained stages. Each stage builds on the previous — from a basic API call to fine-tuned models deployed in production.

## 📁 Learning Stages

| Day | Folder | Description | Status |
|-----|--------|-------------|--------|
| 1 | [`basicllm/`](basicllm/README.md) | Basic Claude API connection, question-answer loop | ✅ Complete |
| 2 | [`llm_intuition/`](llm_intuition/README.md) | Temperature, context limits, failure modes | ✅ Complete |
| 3 | [`tokens_and_models/`](tokens_and_models/README.md) | Token counting, model tiers (Haiku/Sonnet/Opus), cost estimation | ✅ Complete |
| 4 | [`reliable_api_calls/`](reliable_api_calls/README.md) | Retry logic, timeouts, structured logging, jitter, request IDs, log rotation | ✅ Complete |
| 5–6 | `prompt_engineering/` | System prompts, few-shot prompting, chain-of-thought, **extended thinking API**, structured outputs with Pydantic, prompt versioning | 📋 Planned |
| 7 | `multi_modal/` | Claude vision API — sending images, PDFs, and screenshots in prompts | 📋 Planned |
| 8–10 | `chatbot_backend/` | FastAPI endpoint, streaming responses, multi-turn memory management, async retries (`asyncio.sleep`), connect vs read timeout, **JWT/OAuth authentication, user-level rate limiting** | 📋 Planned |
| 11–12 | `chatbot_frontend/` | React UI, real-time streaming display, conversation history | 📋 Planned |
| 13 | `embeddings/` | Vector embeddings, cosine similarity, embedding models, intro to vector databases | 📋 Planned |
| 14–16 | `llm_with_rag/` | Document loading, chunking strategies, vector DB (Chroma), semantic search, LangChain / LlamaIndex | 📋 Planned |
| 17–18 | `tool_calling/` | Function calling, tool result handling, idempotency awareness, **MCP (Model Context Protocol)** | 📋 Planned |
| 19–21 | `agents/` | ReAct loops, multi-step reasoning, multi-agent orchestration, LangChain agents | 📋 Planned |
| 22 | `safety_and_guardrails/` | Prompt injection defence, output validation, content filtering, PII handling | 📋 Planned |
| 23–24 | `evals_and_observability/` | Golden test datasets, LLM evals, LangSmith tracing, circuit breaker pattern | 📋 Planned |
| 25 | `cost_optimization/` | Prompt caching (cache_control), **semantic caching** (embedding-based), model routing, batch API, fallback model (Opus → Sonnet) | 📋 Planned |
| 26–28 | `fullstack_app/` | Complete application integrating all components built so far | 📋 Planned |
| 29 | `deployment/` | Docker, environment management, secrets in production, CI/CD for LLM apps, monitoring | 📋 Planned |
| 30+ | `fine_tuning/` | Dataset preparation, fine-tuning API, evaluation, comparing base vs fine-tuned model | 📋 Planned |

## 🗺️ Learning Path Overview

```
Foundations          Reliability          Prompting            Interfaces
──────────           ───────────          ─────────            ──────────
Day 1 Basic API  →  Day 4 Retry/    →  Day 5-6 Prompt   →  Day 8-10 Backend
Day 2 Intuition      Timeout/Log        Engineering          Day 11-12 Frontend
Day 3 Tokens                        Day 7 Multi-modal
                                                             ↓
                                                        Knowledge
                                                        ─────────
                                                        Day 13 Embeddings
                                                        Day 14-16 RAG +
                                                          LangChain
                                                             ↓
                                                        Autonomy
                                                        ────────
                                                        Day 17-18 Tools
                                                        Day 19-21 Agents
                                                             ↓
                                                        Production
                                                        ──────────
                                                        Day 22 Safety
                                                        Day 23-24 Evals
                                                        Day 25 Cost
                                                        Day 26-28 Fullstack
                                                        Day 29 Deploy
                                                        Day 30+ Fine-tune
```

## 🚀 Next Stage: Prompt Engineering (Day 5–6)

```bash
cd prompt_engineering
pip3 install -r requirements.txt
cp .env.example .env
# Add your Claude API key to .env (get from https://console.anthropic.com/)
python3 prompt_engineering.py
```

## 🔧 Setup Details

- **Python**: 3.9+
- **LLM**: Claude Haiku 4.5 · Sonnet 4.5 · Opus 4.5 (via Anthropic API)
- **Dependencies**: `anthropic>=0.7.0`, `python-dotenv>=1.0.0`
- **Input**: Interactive menu — each stage has its own explorer

## 🧠 Key Learnings from Development

### Tokens Are Not Characters (Day 3)
~4 English characters ≈ 1 token for content, but every API call adds ~5–7 structural tokens (role headers, turn delimiters) as fixed overhead. Use `count_tokens()` before sending long prompts to budget cost upfront.

### Model Routing Matters (Day 3)
Haiku is consistently the fastest and cheapest. Sonnet is most token-efficient for factual tasks. Opus over-delivers even on simple tasks and costs ~18× more than Haiku. Route tasks to the cheapest model that meets quality requirements.

### Output Tokens Drive Cost (Day 3)
Output tokens are 5× more expensive than input tokens across all model tiers. `max_tokens` is a hard ceiling — responses cut off mid-sentence when hit. Set it generously and let the model choose its natural stopping point.

### Retry Without Jitter Is Dangerous (Day 4)
Plain exponential backoff (1s, 2s, 4s…) causes a thundering herd — all clients retry at the same instant and make the overload worse. Adding `random(0,1)s` jitter spreads retries across time.

### Cap Your Backoff (Day 4)
Without a `max_wait` ceiling, attempt 10 with `backoff_factor=2` waits 512 seconds. Production systems cap at 60s.

### Respect Retry-After Headers (Day 4)
On 429 rate-limit responses the API often sends a `Retry-After` header with the exact wait time. Always read it first before falling back to computed backoff.

### Correlation IDs Are Non-Negotiable at Scale (Day 4)
Without a shared `request_id` on every log entry for one call, logs become ungreppable at volume. Every call should generate a UUID and stamp it on all its log lines.

### API Evolution & Model Names
LLM APIs evolve rapidly — model names change frequently. Always verify available models via API calls using `client.models.list()`.

### Environment Variable Management
`python-dotenv` simplifies `.env` file loading. Never hardcode API keys — use `load_dotenv()` + `os.getenv("API_KEY")`.

### Dependency Management
Use `requirements.txt` for reproducible environments. Specify minimum versions and use platform-appropriate commands (`pip3` on macOS).

## 📦 Package Structure

```
basicllm/                   # Day 1: Basic LLM connection
├── __init__.py
├── llm_basic.py
├── requirements.txt
├── .env.example
├── README.md
└── LEARNINGS.md

llm_intuition/              # Day 2: LLM intuition exploration
├── __init__.py
├── llm_intuition.py
├── requirements.txt
├── .env.example
├── README.md
└── LEARNINGS.md

tokens_and_models/          # Day 3: Token counting, model comparison, cost estimation
├── __init__.py
├── tokens_and_models.py
├── requirements.txt
├── .env.example
├── README.md
└── LEARNINGS.md

reliable_api_calls/         # Day 4: Retry, timeout, logging, jitter, request IDs, rotation
├── __init__.py
├── reliable_api_calls.py
├── requirements.txt
├── .env.example
├── README.md
└── LEARNINGS.md
```

Each stage is self-contained with its own dependencies and setup.
