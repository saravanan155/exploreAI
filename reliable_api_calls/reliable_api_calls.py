"""
Reliable API Calls Explorer
Day 4: Retry logic, timeouts, and structured logging for production-ready LLM calls.
"""

import json
import logging
import logging.handlers
import os
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
MODELS = {
    "haiku":  "claude-haiku-4-5",
    "sonnet": "claude-sonnet-4-5",
    "opus":   "claude-opus-4-5",
}

# ---------------------------------------------------------------------------
# Pricing  (USD per 1 million tokens – Anthropic list prices, April 2026)
# Keys match a substring of the model name returned by the API.
# ---------------------------------------------------------------------------
_PRICING = {
    "haiku":  {"input": 0.80,  "output": 4.00},
    "sonnet": {"input": 3.00,  "output": 15.00},
    "opus":   {"input": 15.00, "output": 75.00},
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> dict:
    """
    Calculate the real USD cost of an API call from actual token counts.

    Args:
        model:         Model name as returned by the API (e.g. 'claude-haiku-4-5-…').
        input_tokens:  Actual input tokens used (from response.usage).
        output_tokens: Actual output tokens used (from response.usage).

    Returns:
        dict with keys: input_cost, output_cost, total_cost, rate_input, rate_output
    """
    model_lower = model.lower()
    rates = None
    for key, pricing in _PRICING.items():
        if key in model_lower:
            rates = pricing
            break
    if rates is None:
        raise ValueError(f"No pricing found for model: {model}")

    input_cost  = (input_tokens  / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    return {
        "input_cost":   input_cost,
        "output_cost":  output_cost,
        "total_cost":   input_cost + output_cost,
        "rate_input":   rates["input"],
        "rate_output":  rates["output"],
    }

# ---------------------------------------------------------------------------
# Structured logger – console (human-readable) + file (JSON)
# ---------------------------------------------------------------------------
LOG_FILE = "api_calls.log"


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        # Standard fields skipped from JSON extras
        _SKIP = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
            "taskName",
        }
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for key, val in record.__dict__.items():
            if key not in _SKIP:
                entry[key] = val
        return json.dumps(entry)


def setup_logger(log_file: str = LOG_FILE) -> logging.Logger:
    """
    Configure a dual-output logger:
      - Console : human-readable single-line format
      - File    : one JSON object per line (machine-readable)
    """
    logger = logging.getLogger("reliable_api")
    if logger.handlers:           # avoid duplicate handlers on re-init
        return logger
    logger.setLevel(logging.DEBUG)

    # Console – human-readable
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(
        logging.Formatter(
            "%(asctime)s  [%(levelname)-8s]  %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logger.addHandler(ch)

    # File – JSON, rotates at 5 MB, keeps 3 backups
    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_JsonFormatter())
    logger.addHandler(fh)

    return logger


_logger = setup_logger()


# ---------------------------------------------------------------------------
# Client helper
# ---------------------------------------------------------------------------
def _get_client(timeout: float = 30.0) -> anthropic.Anthropic:
    """Return an authenticated Anthropic client with the given timeout."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Add it to .env.")
    return anthropic.Anthropic(api_key=api_key, timeout=timeout)


# ---------------------------------------------------------------------------
# Core call (builds on Day 3)
# ---------------------------------------------------------------------------
def call_llm(
    question: str,
    model: str = "claude-haiku-4-5",
    temperature: float = 0.7,
    max_tokens: int = 500,
    timeout: float = 30.0,
) -> dict:
    """
    Make a single API call and return the response + usage metadata.

    Args:
        question:    Prompt to send.
        model:       Model identifier.
        temperature: Randomness (0.0–1.0).
        max_tokens:  Hard ceiling on output tokens.
        timeout:     Seconds before raising APITimeoutError.

    Returns:
        dict with keys: text, input_tokens, output_tokens, total_tokens,
                        model, latency_s
    """
    client = _get_client(timeout=timeout)
    start = time.perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": question}],
    )
    latency = round(time.perf_counter() - start, 2)
    return {
        "text": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "model": response.model,
        "latency_s": latency,
    }


# ---------------------------------------------------------------------------
# Retry wrapper
# ---------------------------------------------------------------------------

# Errors that are safe to retry (transient / network / rate-limit)
_RETRYABLE_ERRORS = (
    anthropic.RateLimitError,
    anthropic.APIConnectionError,
    anthropic.APITimeoutError,
)


def _compute_wait(
    attempt: int,
    backoff_factor: float,
    max_wait: float,
    with_jitter: bool,
) -> float:
    """
    Calculate how long to wait before the next retry.

    Formula: min(max_wait, backoff_factor ^ (attempt-1)) [+ jitter]

    Args:
        attempt:       Current attempt number (1-based).
        backoff_factor: Multiplier — doubles wait each attempt when factor=2.
        max_wait:      Hard ceiling so waits never grow unbounded.
        with_jitter:   If True, adds random(0, 1) seconds to spread retries
                       across time and avoid the thundering herd problem.
    """
    wait = min(max_wait, backoff_factor ** (attempt - 1))
    if with_jitter:
        wait += random.uniform(0, 1)
    return wait


def _get_retry_after_wait(exc: Exception, fallback: float) -> float:
    """
    Read the Retry-After header from a 429 RateLimitError response.

    When the API sends a Retry-After header it tells you *exactly* how long
    to wait — more accurate than a computed backoff. Falls back to the
    computed value if the header is absent or unreadable.

    Args:
        exc:      The RateLimitError raised by the Anthropic SDK.
        fallback: Computed backoff value to use if no header is present.
    """
    try:
        header = exc.response.headers.get("retry-after")  # type: ignore[union-attr]
        if header:
            return float(header)
    except Exception:
        pass
    return fallback


def call_llm_with_retry(
    question: str,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    max_wait: float = 60.0,
    with_jitter: bool = True,
    **kwargs,
) -> dict:
    """
    Call the LLM with exponential back-off retry on transient errors.

    Wait schedule (seconds): min(max_wait, backoff_factor^attempt) [+ jitter]

    Retries on:
      - RateLimitError     (429) – respects Retry-After header if present
      - APIConnectionError (network failure)
      - APITimeoutError    (request exceeded timeout)
      - APIStatusError     with status >= 500 (server-side errors)

    Does NOT retry on 4xx client errors (bad request, invalid key, etc.)

    Args:
        question:       Prompt to send.
        max_retries:    Maximum number of attempts (including the first).
        backoff_factor: Multiplier for wait time between retries.
        max_wait:       Hard ceiling on wait time (seconds) so backoff never
                        grows unbounded. Default 60s.
        with_jitter:    Add random(0,1)s to each wait to avoid thundering herd.
        **kwargs:       Forwarded to call_llm().
    """
    last_exc: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            result = call_llm(question, **kwargs)
            if attempt > 1:
                print(f"   ✅ Succeeded on attempt {attempt}")
            return result

        except anthropic.RateLimitError as exc:
            last_exc = exc
            wait = _get_retry_after_wait(
                exc, _compute_wait(attempt, backoff_factor, max_wait, with_jitter)
            )
            print(
                f"   ⚠️  Attempt {attempt}/{max_retries} failed "
                f"(RateLimitError). Retrying in {wait:.2f}s…"
            )
            if attempt < max_retries:
                time.sleep(wait)

        except (anthropic.APIConnectionError, anthropic.APITimeoutError) as exc:
            last_exc = exc
            wait = _compute_wait(attempt, backoff_factor, max_wait, with_jitter)
            print(
                f"   ⚠️  Attempt {attempt}/{max_retries} failed "
                f"({type(exc).__name__}). Retrying in {wait:.2f}s…"
            )
            if attempt < max_retries:
                time.sleep(wait)

        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500:
                last_exc = exc
                wait = _compute_wait(attempt, backoff_factor, max_wait, with_jitter)
                print(
                    f"   ⚠️  Attempt {attempt}/{max_retries} failed "
                    f"(HTTP {exc.status_code}). Retrying in {wait:.2f}s…"
                )
                if attempt < max_retries:
                    time.sleep(wait)
            else:
                raise   # 4xx (except 429) are client errors – don't retry

    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Timeout wrapper
# ---------------------------------------------------------------------------
def call_llm_with_timeout(
    question: str,
    timeout_seconds: float = 10.0,
    **kwargs,
) -> dict:
    """
    Call the LLM with an explicit timeout.

    Raises anthropic.APITimeoutError if the request takes longer than
    timeout_seconds. This prevents a slow API from hanging your application
    indefinitely.

    Args:
        question:        Prompt to send.
        timeout_seconds: Maximum seconds to wait for a response.
        **kwargs:        Forwarded to call_llm().
    """
    return call_llm(question, timeout=timeout_seconds, **kwargs)


# ---------------------------------------------------------------------------
# Logged call
# ---------------------------------------------------------------------------
def call_llm_logged(
    question: str,
    logger: Optional[logging.Logger] = None,
    request_id: Optional[str] = None,
    **kwargs,
) -> dict:
    """
    Call the LLM and emit a structured log entry for both success and failure.

    Every call generates (or accepts) a unique request_id so that the
    '→ Sending' and '← Succeeded' log entries can be correlated in a log
    aggregator even when thousands of calls are interleaved.

    Log fields on success : request_id, prompt_preview, model, input_tokens,
                            output_tokens, total_tokens, latency_s, cost_usd, status
    Log fields on failure : request_id, prompt_preview, error_type, error_message, status

    Args:
        question:    Prompt to send.
        logger:      Logger instance (defaults to the module logger).
        request_id:  Unique ID for this call (auto-generated UUID4 if omitted).
        **kwargs:    Forwarded to call_llm().
    """
    log = logger or _logger
    rid = request_id or str(uuid.uuid4())
    preview = question[:80].replace("\n", " ")
    log.info(f"→ Sending prompt: '{preview}…'", extra={"request_id": rid})

    try:
        result = call_llm(question, **kwargs)
        cost = calculate_cost(
            result["model"], result["input_tokens"], result["output_tokens"]
        )
        log.info(
            "← API call succeeded",
            extra={
                "request_id": rid,
                "prompt_preview": preview,
                "model": result["model"],
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "total_tokens": result["total_tokens"],
                "latency_s": result["latency_s"],
                "cost_usd": round(cost["total_cost"], 8),
                "status": "success",
            },
        )
        result["cost"] = cost
        result["request_id"] = rid
        return result

    except Exception as exc:
        log.error(
            f"← API call failed: {exc}",
            extra={
                "request_id": rid,
                "prompt_preview": preview,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "status": "error",
            },
        )
        raise


# ---------------------------------------------------------------------------
# Reliable call – retry + timeout + logging combined
# ---------------------------------------------------------------------------
def call_llm_reliable(
    question: str,
    max_retries: int = 3,
    timeout_seconds: float = 30.0,
    backoff_factor: float = 2.0,
    max_wait: float = 60.0,
    with_jitter: bool = True,
    logger: Optional[logging.Logger] = None,
    **kwargs,
) -> dict:
    """
    Production-ready LLM call: retry + timeout + structured logging.

    Combines:
      - Exponential back-off with jitter and a max-wait ceiling
      - Retry-After header respect on 429 responses
      - Hard per-attempt timeout
      - Structured JSON logging with a shared request_id across all entries

    Args:
        question:        Prompt to send.
        max_retries:     Maximum number of attempts.
        timeout_seconds: Per-attempt timeout.
        backoff_factor:  Multiplier for back-off wait time.
        max_wait:        Hard ceiling on wait between retries (seconds).
        with_jitter:     Add random(0,1)s to back-off to avoid thundering herd.
        logger:          Logger instance (defaults to module logger).
        **kwargs:        Forwarded to call_llm().
    """
    log = logger or _logger
    rid = str(uuid.uuid4())
    preview = question[:80].replace("\n", " ")
    last_exc: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            result = call_llm(question, timeout=timeout_seconds, **kwargs)
            log.info(
                f"← Reliable call succeeded (attempt {attempt})",
                extra={
                    "request_id": rid,
                    "prompt_preview": preview,
                    "attempt": attempt,
                    "model": result["model"],
                    "input_tokens": result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                    "latency_s": result["latency_s"],
                    "status": "success",
                },
            )
            result["request_id"] = rid
            return result

        except anthropic.RateLimitError as exc:
            last_exc = exc
            wait = _get_retry_after_wait(
                exc, _compute_wait(attempt, backoff_factor, max_wait, with_jitter)
            )
            log.warning(
                f"Attempt {attempt}/{max_retries} failed (RateLimitError). "
                f"Retrying in {wait:.2f}s…",
                extra={"request_id": rid, "attempt": attempt, "wait_s": wait},
            )
            if attempt < max_retries:
                time.sleep(wait)

        except (anthropic.APIConnectionError, anthropic.APITimeoutError) as exc:
            last_exc = exc
            wait = _compute_wait(attempt, backoff_factor, max_wait, with_jitter)
            log.warning(
                f"Attempt {attempt}/{max_retries} failed ({type(exc).__name__}). "
                f"Retrying in {wait:.2f}s…",
                extra={"request_id": rid, "attempt": attempt, "error_type": type(exc).__name__, "wait_s": wait},
            )
            if attempt < max_retries:
                time.sleep(wait)

        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500:
                last_exc = exc
                wait = _compute_wait(attempt, backoff_factor, max_wait, with_jitter)
                log.warning(
                    f"Attempt {attempt}/{max_retries} failed (HTTP {exc.status_code}). "
                    f"Retrying in {wait:.2f}s…",
                    extra={"request_id": rid, "attempt": attempt, "status_code": exc.status_code, "wait_s": wait},
                )
                if attempt < max_retries:
                    time.sleep(wait)
            else:
                log.error(
                    f"Non-retryable error: HTTP {exc.status_code}",
                    extra={"request_id": rid, "status_code": exc.status_code, "status": "error"},
                )
                raise

        except Exception as exc:
            log.error(
                str(exc),
                extra={"request_id": rid, "error_type": type(exc).__name__, "status": "error"},
            )
            raise

    log.error(
        f"All {max_retries} attempts exhausted.",
        extra={"request_id": rid, "max_retries": max_retries, "status": "error"},
    )
    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Demo / test functions
# ---------------------------------------------------------------------------
_DEMO_PROMPT = "In one sentence, what is exponential backoff?"


def test_retry_logic() -> None:
    """Demonstrate retry behaviour using a simulated flaky API call."""
    print("\n" + "=" * 60)
    print("RETRY LOGIC DEMO")
    print("=" * 60)
    print("Simulating an API that fails 2 times before succeeding.")
    print(f"📝 Prompt: {_DEMO_PROMPT}\n")

    fail_counter = {"remaining": 2}

    # A local wrapper that fails `remaining` times then delegates to real call_llm
    def _flaky_call(question: str, **kwargs) -> dict:
        if fail_counter["remaining"] > 0:
            fail_counter["remaining"] -= 1
            raise ConnectionError(
                f"Simulated transient network error "
                f"(failures left: {fail_counter['remaining']})"
            )
        return call_llm(question, **kwargs)

    # Local retry loop so the demo is fully self-contained
    max_retries = 4
    backoff_factor = 1.0  # 1s gaps so the demo runs quickly
    last_exc: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            result = _flaky_call(_DEMO_PROMPT)
            if attempt > 1:
                print(f"   ✅ Succeeded on attempt {attempt}")
            print(f"\n📨 Response : {result['text'][:120]}")
            print(f"📊 Tokens   : {result['total_tokens']} | Latency: {result['latency_s']}s")
            break
        except Exception as exc:
            last_exc = exc
            wait = backoff_factor ** (attempt - 1)
            print(
                f"   ⚠️  Attempt {attempt}/{max_retries} failed: {exc}. "
                f"Retrying in {wait:.0f}s…"
            )
            if attempt < max_retries:
                time.sleep(wait)
    else:
        print(f"\n❌ All {max_retries} attempts failed. Last error: {last_exc}")

    print("\n💡 Key insight: Exponential backoff (1s → 2s → 4s…) prevents hammering")
    print("   an overloaded API and gives it time to recover between retries.")
    print("   Only retry transient errors — never retry bad requests or auth failures.")


def test_timeout() -> None:
    """Show what happens when a timeout is hit vs. a healthy call."""
    print("\n" + "=" * 60)
    print("TIMEOUT DEMO")
    print("=" * 60)
    print("Testing the same prompt with two different timeout values.")
    print(f"📝 Prompt: {_DEMO_PROMPT}\n")

    cases = [
        (0.001, "Extremely short → forces APITimeoutError"),
        (30.0,  "Normal (30s)    → should succeed        "),
    ]

    for timeout_s, label in cases:
        print(f"⏱  {label}  (timeout={timeout_s}s)")
        try:
            result = call_llm_with_timeout(_DEMO_PROMPT, timeout_seconds=timeout_s)
            print(f"   ✅ Responded in {result['latency_s']}s — {result['total_tokens']} tokens used")
        except anthropic.APITimeoutError:
            print(f"   ⏰ APITimeoutError — request exceeded {timeout_s}s and was cancelled")
        except Exception as exc:
            print(f"   ❌ {type(exc).__name__}: {exc}")
        print()

    print("💡 Key insight: Always set a timeout. Without one, a slow or hung API")
    print("   call will block your application thread indefinitely.")
    print("   30s is a sensible default for most LLM calls.")


def test_structured_logging() -> None:
    """Show what structured log output looks like on console and in the log file."""
    print("\n" + "=" * 60)
    print("STRUCTURED LOGGING DEMO")
    print("=" * 60)
    print("Making an API call with full logging enabled.")
    print(f"Console output → human-readable")
    print(f"File output    → {LOG_FILE} (one JSON object per line)")
    print(f"📝 Prompt: {_DEMO_PROMPT}\n")

    result = call_llm_logged(_DEMO_PROMPT)

    # Display real cost breakdown
    cost = result["cost"]
    print(f"\n💰 Real cost breakdown for this call:")
    print(f"   Model          : {result['model']}")
    print(f"   Input tokens   : {result['input_tokens']:>6}  × ${cost['rate_input']:.2f}/1M = ${cost['input_cost']:.8f}")
    print(f"   Output tokens  : {result['output_tokens']:>6}  × ${cost['rate_output']:.2f}/1M = ${cost['output_cost']:.8f}")
    print(f"   ─────────────────────────────────────────────────────")
    print(f"   Total cost     :                          ${cost['total_cost']:.8f}")
    print(f"   (≈ ${cost['total_cost'] * 1000:.6f} per 1,000 identical calls)")

    # Show the last JSON entry written to the log file
    print(f"\n📄 Latest entry written to {LOG_FILE}:")
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        raw_line = lines[-1]
        last = json.loads(raw_line)

        print("\n  Raw (as stored in file):")
        print(f"  {raw_line}")

        print("\n  Formatted (pretty-printed):")
        print(json.dumps(last, indent=2))
    except (FileNotFoundError, IndexError, json.JSONDecodeError) as exc:
        print(f"   (Could not read log file: {exc})")

    print("\n💡 Key insight: Structured JSON logs can be ingested by observability")
    print("   tools (Datadog, CloudWatch, Grafana Loki) for dashboards and alerts.")
    print("   Always log: timestamp, model, tokens, latency, and success/failure.")


def test_reliable_call() -> None:
    """Show the combined retry + timeout + logging in one production-style call."""
    print("\n" + "=" * 60)
    print("RELIABLE CALL DEMO  (retry + timeout + logging)")
    print("=" * 60)
    _reliable_prompt = "Explain what a REST API is in two sentences."
    print("Making a production-style call with all reliability features.")
    print(f"📝 Prompt: {_reliable_prompt}\n")

    result = call_llm_reliable(
        _reliable_prompt,
        max_retries=3,
        timeout_seconds=30.0,
        backoff_factor=2.0,
    )
    print(f"\n📨 Response:\n{result['text']}")
    print(
        f"\n📊 Usage: {result['input_tokens']} in / {result['output_tokens']} out"
        f" / {result['total_tokens']} total | {result['latency_s']}s"
    )
    print("\n💡 Key insight: call_llm_reliable() is the function you'd use in")
    print("   production. It gives you resilience (retry), safety (timeout),")
    print("   and observability (logging) for free at every call site.")


def test_advanced_reliability() -> None:
    """Demonstrate all five advanced reliability features side-by-side."""
    print("\n" + "=" * 60)
    print("ADVANCED RELIABILITY DEMO")
    print("=" * 60)
    print("Covering: jitter, max_wait cap, Retry-After, request_id, log rotation\n")

    # ── 1. Jitter ──────────────────────────────────────────────────────────
    print("─" * 60)
    print("1️⃣  JITTER  — prevents thundering herd")
    print("   Without jitter: all clients retry at exactly the same second.")
    print("   With jitter   : each client adds random(0,1)s to spread retries.\n")
    print("   Simulated wait times for 5 failed attempts (backoff_factor=2, max_wait=60):\n")
    print(f"   {'Attempt':<10} {'Without jitter':>16} {'With jitter':>16}")
    print(f"   {'─'*10} {'─'*16} {'─'*16}")
    for attempt in range(1, 6):
        no_jitter = _compute_wait(attempt, 2.0, 60.0, with_jitter=False)
        jitter    = _compute_wait(attempt, 2.0, 60.0, with_jitter=True)
        print(f"   {attempt:<10} {no_jitter:>15.2f}s {jitter:>15.2f}s")

    # ── 2. Max Wait Cap ────────────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print("2️⃣  MAX WAIT CAP  — backoff never grows unbounded")
    print("   Without cap: attempt 10 with factor=2 would wait 512 seconds.")
    print("   With cap=60: waits plateau at 60s regardless of attempt number.\n")
    print(f"   {'Attempt':<10} {'Uncapped':>12} {'Capped at 60s':>16}")
    print(f"   {'─'*10} {'─'*12} {'─'*16}")
    for attempt in range(1, 12):
        uncapped = 2.0 ** (attempt - 1)
        capped   = _compute_wait(attempt, 2.0, 60.0, with_jitter=False)
        print(f"   {attempt:<10} {uncapped:>11.1f}s {capped:>15.1f}s")

    # ── 3. Retry-After Header ──────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print("3️⃣  RETRY-AFTER HEADER  — use the server's own wait time on 429s")
    print("   When the API returns HTTP 429 it may include:")
    print("     Retry-After: 45")
    print("   _get_retry_after_wait() reads this and waits exactly 45s instead")
    print("   of the computed backoff. Falls back to computed value if absent.")
    print("\n   Code path:")
    print("     wait = _get_retry_after_wait(exc, computed_fallback)")
    print("     # → returns float(header) if present, else computed_fallback")

    # ── 4. Correlation / Request ID ────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print("4️⃣  REQUEST ID  — correlate log entries for the same call")
    print("   Making a logged call and showing the shared request_id...\n")
    result = call_llm_logged(_DEMO_PROMPT)
    rid = result["request_id"]
    print(f"\n   request_id: {rid}")
    print("   ↑ This same ID appears on BOTH the '→ Sending' and")
    print("     '← Succeeded' log lines, so you can grep logs by request_id")
    print("     and see the full story for any single call.")

    # ── 5. Log Rotation ────────────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print("5️⃣  LOG ROTATION  — log file never grows unbounded")
    print(f"   {LOG_FILE} is managed by RotatingFileHandler:")
    print(f"   • Max size  : 5 MB per file")
    print(f"   • Backups   : 3  (api_calls.log.1, .2, .3)")
    print(f"   • Behaviour : when file hits 5 MB it is renamed to .1,")
    print(f"     a new api_calls.log is created, oldest backup is deleted.")
    print(f"   • Without rotation a long-running app would fill the disk.")

    print(f"\n{'=' * 60}")
    print("💡 Summary — what each feature protects against:")
    print("   Jitter        → thundering herd (all clients retry at once)")
    print("   Max wait cap  → unbounded backoff (512s waits in production)")
    print("   Retry-After   → waiting wrong amount on rate limits")
    print("   Request ID    → untraceable log entries at scale")
    print("   Log rotation  → disk exhaustion in long-running apps")


# ---------------------------------------------------------------------------
# Interactive menu
# ---------------------------------------------------------------------------
def interactive_mode() -> None:
    print("\n" + "=" * 60)
    print("INTERACTIVE RELIABLE API CALLS EXPLORER")
    print("=" * 60)

    while True:
        print("\nOptions:")
        print("1. Retry Logic Demo")
        print("2. Timeout Demo")
        print("3. Structured Logging Demo")
        print("4. Reliable Call Demo  (retry + timeout + logging)")
        print("5. Advanced Reliability Demo  (jitter, max_wait, Retry-After, request_id, log rotation)")
        print("6. Custom Prompt       (uses call_llm_reliable)")
        print("7. Exit")

        choice = input("\nChoose an option (1-7): ").strip()

        if choice == "1":
            test_retry_logic()
        elif choice == "2":
            test_timeout()
        elif choice == "3":
            test_structured_logging()
        elif choice == "4":
            test_reliable_call()
        elif choice == "5":
            test_advanced_reliability()
        elif choice == "6":
            prompt = input("Enter your prompt: ").strip()
            model_choice = (
                input("Model [haiku/sonnet/opus] (default: haiku): ")
                .strip()
                .lower()
                or "haiku"
            )
            model_id = MODELS.get(model_choice, MODELS["haiku"])
            max_tok = int(input("Max tokens (default 500): ").strip() or "500")
            print(f"\n📝 Prompt  : {prompt}")
            print(f"🤖 Model   : {model_id}")
            print(f"🔢 Max tok : {max_tok}\n")
            try:
                result = call_llm_reliable(
                    prompt,
                    model=model_id,
                    max_tokens=max_tok,
                    max_retries=3,
                    timeout_seconds=30.0,
                )
                print(f"\nResponse:\n{result['text']}")
                print(
                    f"\n📊 Usage: {result['input_tokens']} in / "
                    f"{result['output_tokens']} out / "
                    f"{result['total_tokens']} total | {result['latency_s']}s"
                )
            except Exception as exc:
                print(f"Error: {exc}")
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def main() -> None:
    print("=" * 60)
    print("🔁 RELIABLE API CALLS EXPLORER (Day 4)")
    print("=" * 60)
    print("Learn retry logic, timeouts, and structured logging!")
    interactive_mode()


if __name__ == "__main__":
    main()













