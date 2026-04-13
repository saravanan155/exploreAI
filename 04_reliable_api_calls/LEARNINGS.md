# Reliable API Calls – Development Notes

## 🎯 Day 4 Focus: Reliable API Calls
**Goal:** Make LLM calls production-ready with retry logic, timeouts, structured logging, and advanced reliability patterns
**Started:** April 8, 2026

## 📈 Development Journey

### Building on Day 3 (tokens_and_models)
- ✅ Copied package structure from `tokens_and_models/`
- ✅ Renamed to `reliable_api_calls.py`
- ✅ Retained `call_llm()` as the core call — added `timeout` parameter
- ✅ Added `_get_client()` helper that injects timeout at the SDK level

### Phase 1: Retry Logic
- ✅ Identified retryable vs. non-retryable Anthropic errors
- ✅ Implemented `call_llm_with_retry()` with exponential back-off
- ✅ Built `test_retry_logic()` using a simulated flaky wrapper (no real API errors needed)

### Phase 2: Timeout Control
- ✅ Used Anthropic SDK's built-in `timeout` parameter (backed by `httpx`)
- ✅ Implemented `call_llm_with_timeout()` as a thin wrapper
- ✅ Built `test_timeout()` to show both forced failure (0.001s) and success (30s)

### Phase 3: Structured Logging
- ✅ Built `_JsonFormatter` — emits one JSON object per log record to file
- ✅ Dual handler: human-readable console + JSON file (`api_calls.log`)
- ✅ Implemented `call_llm_logged()` — logs prompt preview, tokens, latency, cost, status
- ✅ Built `test_structured_logging()` to show raw + formatted log output and real cost breakdown

### Phase 4: Reliable Call
- ✅ Implemented `call_llm_reliable()` — combines retry + timeout + logging
- ✅ This is the function to use in production at every call site
- ✅ Built `test_reliable_call()` to demonstrate the combined pattern

### Phase 5: Advanced Reliability
- ✅ Added `_compute_wait()` with jitter and max_wait cap
- ✅ Added `_get_retry_after_wait()` to read Retry-After header from 429 responses
- ✅ Added UUID4 `request_id` / correlation ID to `call_llm_logged()` and `call_llm_reliable()`
- ✅ Switched `FileHandler` → `RotatingFileHandler` (5 MB cap, 3 backups)
- ✅ Built `test_advanced_reliability()` to demonstrate all five features side-by-side

### Phase 6: Cost Calculation & Display
- ✅ Added `_PRICING` table with real Anthropic per-million-token rates
- ✅ Implemented `calculate_cost()` — computes exact USD from actual token counts
- ✅ Integrated into `call_llm_logged()` — cost appears in log entry and is displayed in option 3
- ✅ Option 3 shows real cost breakdown: input cost + output cost + total + cost per 1,000 calls

### Phase 7: Interactive Interface
- ✅ 7-option menu system (expanded from initial 6)
- ✅ All options display the request prompt before sending (`📝 Prompt:`)
- ✅ Custom prompt mode (option 6) echoes back prompt, model, and max_tokens before calling
- ✅ Graceful error handling throughout

## 🧠 Key Learnings from Day 4

### 1. **Not All Errors Are Worth Retrying**
- **Retryable (transient):** `RateLimitError` (429), `APIConnectionError`, `APITimeoutError`, 5xx server errors
- **Not retryable (client errors):** 400 Bad Request, 401 Unauthorised, 404 Not Found
- **Rule:** Retry errors the *server* caused; don't retry errors *you* caused

### 2. **Exponential Back-off with Jitter & Cap**
- **Formula:** `wait = min(max_wait, backoff_factor ^ (attempt - 1)) + random(0, 1)`
- **Without jitter:** All clients retry at the exact same second → thundering herd makes overload worse
- **Without cap:** Attempt 10 with factor=2 waits 512s. Cap at 60s in production.
- **With both:** `1.4s, 2.7s, 4.2s, 8.1s … 60s` — safe, spread, bounded

### 3. **Retry-After Header**
- **Learning:** On 429 responses the API sends a `Retry-After` header with the exact wait time
- **Implementation:** `_get_retry_after_wait()` reads the header first, falls back to computed backoff if absent
- **Why better:** The server knows its own load better than your backoff formula

### 4. **Timeouts Are Non-Negotiable**
- **Learning:** Without a timeout, a hung API call blocks your thread indefinitely
- **SDK support:** Anthropic's Python SDK accepts `timeout` at client or per-request level (backed by `httpx`)
- **Rule of thumb:** 30s for standard calls, 60s for long-form generation
- **Async note:** Use `asyncio.sleep()` instead of `time.sleep()` in async applications (Day 8–10)

### 5. **Structured Logging**
- **Learning:** Plain-text logs are hard to query at scale; JSON logs can be ingested by Datadog / CloudWatch / Grafana Loki
- **Always log:** timestamp, model, input_tokens, output_tokens, latency_s, cost_usd, request_id, status
- **Dual handler pattern:** Console for humans during development; file for machines in production
- **Raw vs Formatted:** Raw = single compact JSON line on disk (greppable); Formatted = pretty-printed for humans

### 6. **Request / Correlation ID**
- **Learning:** Without a shared `request_id`, logs for the same call are impossible to correlate at scale
- **Implementation:** `uuid.uuid4()` generated per call, stamped on every log entry (`→ Sending` and `← Succeeded`)
- **Usage:** `grep request_id api_calls.log` shows the full story for any single call

### 7. **Log Rotation**
- **Learning:** `FileHandler` grows the log file unbounded — will fill the disk in production
- **Solution:** `RotatingFileHandler(maxBytes=5*1024*1024, backupCount=3)` — caps at 5 MB, keeps `.1`, `.2`, `.3` backups
- **When full:** Current file renamed to `.1`, fresh file created, oldest backup deleted

### 8. **Real Cost Calculation**
- **Learning:** You can calculate exact USD cost from actual token counts × published pricing
- **Implementation:** `calculate_cost()` resolves model name → pricing tier → `(tokens / 1M) × rate`
- **Output tokens dominate:** 5× more expensive than input tokens across all tiers
- **Display:** Option 3 shows per-call breakdown: input cost + output cost + total + cost per 1,000 calls

### 9. **`call_llm_reliable()` is the Production Pattern**
- **Learning:** Every API call in a real app should go through retry + timeout + logging
- **Signature now includes:** `max_wait`, `with_jitter`, `request_id` (auto-generated UUID4)
- **Extension points:** Add circuit breaker (Day 23–24), fallback model (Day 25), async (Day 8–10)

### Python Concepts Learned Along the Way
- **`time.perf_counter()`** — high-resolution timer for measuring API latency (nanosecond precision, unaffected by clock sync)
- **Default parameter values** — `def call_llm(question, model="claude-haiku-4-5", timeout=30.0)` — if not sent, use default
- **`**kwargs` forwarding** — pass-through pattern: `call_llm_reliable()` → `call_llm()` without listing every parameter
- **`logging.Logger` hierarchy** — module-level logger with `getLogger("reliable_api")`, handler dedup check, level filtering
- **Custom `logging.Formatter`** — `_JsonFormatter` overrides `format()` to emit one JSON object per log record
- **`uuid.uuid4()`** — generates random UUIDs for correlation IDs — no coordination needed between processes

## 🛠️ Technical Implementation Details

### Retryable Error Hierarchy
```
anthropic.APIError
├── anthropic.APIConnectionError   ← network failure       → retry
├── anthropic.APITimeoutError      ← request exceeded timeout → retry
├── anthropic.RateLimitError       ← 429 too many requests → retry (read Retry-After)
└── anthropic.APIStatusError       ← HTTP error response
    ├── 4xx  →  NOT retried (client errors)
    └── 5xx  →  retried (server errors)
```

### Backoff Formula
```python
def _compute_wait(attempt, backoff_factor, max_wait, with_jitter):
    wait = min(max_wait, backoff_factor ** (attempt - 1))
    if with_jitter:
        wait += random.uniform(0, 1)
    return wait
```

### Retry-After Header Reader
```python
def _get_retry_after_wait(exc, fallback):
    header = exc.response.headers.get("retry-after")
    return float(header) if header else fallback
```

### Structured Log Entry (JSON)
```json
{
  "timestamp": "2026-04-08T10:23:45.123456+00:00",
  "level": "INFO",
  "message": "← API call succeeded",
  "request_id": "d290f410-3bb6-4ad5-8dcd-4b78087aa01d",
  "prompt_preview": "In one sentence, what is exponential backoff?",
  "model": "claude-haiku-4-5-20250514",
  "input_tokens": 18,
  "output_tokens": 42,
  "total_tokens": 60,
  "latency_s": 0.94,
  "cost_usd": 0.00018240,
  "status": "success"
}
```

### `call_llm_reliable()` Signature
```python
def call_llm_reliable(
    question: str,
    max_retries: int = 3,
    timeout_seconds: float = 30.0,
    backoff_factor: float = 2.0,
    max_wait: float = 60.0,
    with_jitter: bool = True,
    logger: Optional[logging.Logger] = None,
    **kwargs,          # forwarded to call_llm: model, temperature, max_tokens
) -> dict:
```

### `calculate_cost()` Signature
```python
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> dict:
    # Returns: {"input_cost", "output_cost", "total_cost", "rate_input", "rate_output"}
```

### `call_llm_logged()` Return Value (enhanced)
```python
{
    "text": "...",
    "input_tokens": 18,
    "output_tokens": 42,
    "total_tokens": 60,
    "model": "claude-haiku-4-5-20250514",
    "latency_s": 0.94,
    "cost": {"input_cost": 0.0000144, "output_cost": 0.000168, "total_cost": 0.0001824, ...},
    "request_id": "d290f410-3bb6-4ad5-8dcd-4b78087aa01d",
}
```

## 📊 Observations

*(To be filled in after running the program)*

### Retry Demo Results:
- Simulated failures:
- Attempts before success:
- Wait times observed:

### Timeout Demo Results:
- 0.001s timeout →
- 30.0s timeout  →

### Structured Logging Demo:
- Console format:
- JSON file fields observed:
- Cost breakdown:

### Advanced Reliability Demo:
- Jitter spread observed:
- Max wait cap at attempt 8+:
- Request ID sample:

## 🚀 Concepts Deferred to Future Days

| # | Concept | Day | Why there |
|---|---|---|---|
| 1 | **Connect vs Read timeout** | Day 8–10 (`chatbot_backend`) | Relevant when building FastAPI services with separate network phases |
| 2 | **Async support** (`asyncio.sleep`) | Day 8–10 (`chatbot_backend`) | FastAPI is async; `time.sleep()` blocks threads |
| 3 | **Idempotency awareness** | Day 17–18 (`tool_calling`) | Safe to retry LLM calls; unsafe to retry tool calls with side effects |
| 4 | **Circuit Breaker pattern** | Day 23–24 (`evals_and_observability`) | Stop retrying entirely after N consecutive failures |
| 5 | **Fallback model** | Day 25 (`cost_optimization`) | Route to cheaper model on primary failure |

## 📈 Success Metrics

- **Functions Implemented:** `call_llm`, `call_llm_with_retry`, `call_llm_with_timeout`, `call_llm_logged`, `call_llm_reliable`, `calculate_cost`, `setup_logger`, `_compute_wait`, `_get_retry_after_wait`
- **Error Types Handled:** RateLimitError (with Retry-After), APIConnectionError, APITimeoutError, APIStatusError (5xx)
- **Log Outputs:** Console (human) + file (JSON with rotation)
- **Menu Options:** 7

## 🎯 Day 4 Objectives

✅ **Retry Logic:** Implement exponential back-off for transient errors
✅ **Timeout:** Set hard per-request timeout to prevent hung calls
✅ **Structured Logging:** Emit machine-readable JSON logs alongside human-readable console output
✅ **Reliable Call:** Combine all three into a single production-ready function
✅ **Error Classification:** Distinguish retryable from non-retryable errors
✅ **Jitter:** Add random offset to back-off to prevent thundering herd
✅ **Max Wait Cap:** Ceiling on back-off so waits never grow unbounded (60s)
✅ **Retry-After Header:** Respect the server's own wait time on 429 responses
✅ **Request / Correlation ID:** Shared UUID4 across all log entries for one call
✅ **Log Rotation:** RotatingFileHandler caps log file at 5 MB, keeps 3 backups
✅ **Cost Calculation:** Real USD cost from actual token counts and Anthropic pricing
✅ **Prompt Display:** All menu options show the request prompt before sending

---

**Development Period:** April 8, 2026
**Status:** ✅ Complete
**Next Stage:** Day 5–6 – Prompt Engineering (system prompts, few-shot, CoT, extended thinking, Pydantic structured outputs, prompt versioning)
