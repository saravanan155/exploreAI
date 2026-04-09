# reliable_api_calls – Reliable API Calls Explorer

Day 4 of the exploreAI project: make LLM calls production-ready with retry logic, timeouts, structured logging, and five advanced reliability patterns.

## 🚀 Quick Start

```bash
cd reliable_api_calls
cp .env.example .env
# Add your Claude API key to .env
python3 reliable_api_calls.py
```

## 🔧 Setup Details

- **Python**: 3.9+
- **LLM**: Claude Haiku 4.5 (default) · Sonnet 4.5 · Opus 4.5
- **Dependencies**: `anthropic>=0.7.0`, `python-dotenv>=1.0.0`
- **Focus**: Resilience, safety, and observability for API calls

## 📦 Package Structure

```
reliable_api_calls/
├── __init__.py                 # Package exports
├── reliable_api_calls.py       # Main script
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── README.md                   # This file
├── LEARNINGS.md                # Development notes and learnings
└── api_calls.log               # Generated at runtime – structured JSON logs
                                # (auto-rotates at 5 MB, 3 backups kept)
```

## 🎯 Features

- ✅ **Retry Logic**: Exponential back-off on rate limits, connection errors, and 5xx responses
- ✅ **Timeout Control**: Hard per-request timeout so a slow API never hangs your app
- ✅ **Structured Logging**: Dual output — human-readable console + machine-readable JSON file
- ✅ **Cost Display**: Real USD cost breakdown (input + output tokens) shown per call
- ✅ **Reliable Call**: Single function combining all three for production use
- ✅ **Jitter**: Random offset added to backoff to prevent thundering herd
- ✅ **Max Wait Cap**: Backoff ceiling (default 60s) so waits never grow unbounded
- ✅ **Retry-After Header**: Reads server's own wait time from 429 responses
- ✅ **Request / Correlation ID**: UUID4 shared across all log entries for one call
- ✅ **Log Rotation**: `RotatingFileHandler` — 5 MB cap, 3 backups, never fills disk

## 📋 Usage

```bash
python3 reliable_api_calls.py
```

### Menu Options:
1. **Retry Logic Demo** – simulates 2 transient failures, shows exponential back-off in action
2. **Timeout Demo** – forces a timeout at 0.001s, then succeeds at 30s
3. **Structured Logging Demo** – live API call with raw + formatted log output and real cost breakdown
4. **Reliable Call Demo** – retry + timeout + logging combined in one production-style call
5. **Advanced Reliability Demo** – side-by-side comparison of jitter, max_wait cap, Retry-After, request_id, and log rotation
6. **Custom Prompt** – your own prompt using `call_llm_reliable()` with all features active
7. **Exit**

### API Examples:

```python
from reliable_api_calls import (
    call_llm_with_retry,
    call_llm_with_timeout,
    call_llm_logged,
    call_llm_reliable,
    calculate_cost,
)

# Retry up to 3 times with jitter and a 60s max wait
result = call_llm_with_retry(
    "What is RAG?",
    max_retries=3,
    backoff_factor=2.0,
    max_wait=60.0,
    with_jitter=True,
)

# Fail fast if the API takes longer than 10 seconds
result = call_llm_with_timeout("What is RAG?", timeout_seconds=10.0)

# Log every call — console + JSON file, with request_id and cost
result = call_llm_logged("What is RAG?")
print(result["request_id"])   # UUID4 shared across both log entries
print(result["cost"])         # {"input_cost": ..., "output_cost": ..., "total_cost": ...}

# Production-ready: all features in one call
result = call_llm_reliable(
    "What is RAG?",
    max_retries=3,
    timeout_seconds=30.0,
    backoff_factor=2.0,
    max_wait=60.0,
    with_jitter=True,
)
print(result["text"], result["total_tokens"], result["latency_s"])
print(result["request_id"])

# Calculate real USD cost from token counts
cost = calculate_cost("claude-haiku-4-5", input_tokens=20, output_tokens=80)
print(f"Total: ${cost['total_cost']:.8f}")
```

## 🔁 Retry Strategy

| Error Type | Retryable? | Wait time |
|---|---|---|
| `RateLimitError` (429) | ✅ Yes | `Retry-After` header if present, else computed backoff |
| `APIConnectionError` | ✅ Yes | Computed backoff + jitter |
| `APITimeoutError` | ✅ Yes | Computed backoff + jitter |
| `APIStatusError` 5xx | ✅ Yes | Computed backoff + jitter |
| `APIStatusError` 4xx | ❌ No | Client error — retrying won't help |

**Backoff formula:** `wait = min(max_wait, backoff_factor ^ (attempt-1)) + random(0,1)`

| Attempt | No jitter | With jitter (example) | Capped at 60s |
|---|---|---|---|
| 1 | 1s | ~1.4s | 1s |
| 2 | 2s | ~2.7s | 2s |
| 3 | 4s | ~4.2s | 4s |
| 8 | 128s | ~128.6s | **60s** |
| 10 | 512s | ~512.3s | **60s** |

## ⚠️ Limitations & Future Work

| Limitation | Status | Planned |
|---|---|---|
| `time.sleep()` blocks the thread | Known | Fixed in Day 8–10 (`chatbot_backend`) with `asyncio.sleep()` |
| Single timeout value (connect + read) | Known | Connect vs read timeout split covered in Day 8–10 |
| No circuit breaker | Known | Covered in Day 23–24 (`evals_and_observability`) |
| No fallback model | Known | Covered in Day 25 (`cost_optimization`) |

## 🎓 Learning Objectives

- Understand which errors are worth retrying and why
- Implement exponential back-off with jitter and a max-wait ceiling
- Read `Retry-After` headers to use the server's own guidance
- Use `request_id` / correlation IDs to trace calls across log entries
- Use Python's `RotatingFileHandler` to prevent log files growing unbounded
- Combine all reliability patterns into a single reusable `call_llm_reliable()` function
- Calculate and log real USD cost per API call

---

**Status:** ✅ Complete
**Day:** 4 of 30
**Last Updated:** April 8, 2026

