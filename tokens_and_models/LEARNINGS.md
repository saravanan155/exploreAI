# Tokens & Models – Development Notes

## 🎯 Day 3 Focus: Tokens & Models
**Goal:** Understand token counting, model tiers (Haiku / Sonnet / Opus), and cost trade-offs  
**Started:** April 7, 2026

## 📈 Development Journey

### Building on Day 2 (llm_intuition)
- ✅ Copied package structure from `llm_intuition/`
- ✅ Renamed to `tokens_and_models.py`
- ✅ Updated package exports (`call_llm`, `count_tokens`, `compare_models`)
- ✅ Enhanced `call_llm()` to return full usage metadata (input/output tokens, latency)

### Phase 1: Token Counting
- ✅ Integrated the Anthropic `messages.count_tokens()` endpoint
- ✅ Built `count_tokens()` helper function
- ✅ Demonstrated character-vs-token differences for English, code, and repeated text
- ✅ Discovered the ~4 chars ≈ 1 token rule of thumb for English

### Phase 2: Model Comparison
- ✅ Defined `MODELS` dict mapping labels → model IDs (Haiku, Sonnet, Opus)
- ✅ Implemented `compare_models()` to fan out to all three tiers
- ✅ Created `test_model_comparison()` with factual, creative, and reasoning prompts
- ✅ Tabulated input tokens, output tokens, total, and latency for easy comparison

### Phase 3: max_tokens Effect
- ✅ Tested limits 50 / 150 / 500 to observe truncation behaviour
- ✅ Observed that Claude never exceeds the requested limit
- ✅ Noted that very low limits can cut off mid-sentence

### Phase 4: Cost Estimation
- ✅ Added static pricing table (approximate, April 2026)
- ✅ Built `test_cost_estimation()` for three realistic workload sizes
- ✅ Shows input cost, output cost, and total cost side-by-side

### Phase 5: Interactive Interface
- ✅ 6-option menu system
- ✅ Custom prompt mode with model and token selection
- ✅ Graceful error handling throughout

## 🧠 Key Learnings from Day 3

### 1. **Tokens vs. Characters**
- **Learning:** Tokens are sub-word units, not characters or words
- **Rule of thumb:** ~4 English characters ≈ 1 token (applies to the *content itself*)
- **Exceptions:** Code, punctuation, non-Latin scripts tokenise differently
- **Tool:** Use `count_tokens()` to check cost before sending long prompts
- **⚠️ Message Structure Overhead:** The `count_tokens()` API counts the *entire message payload*, not just the raw text. Every call includes hidden structural tokens Claude uses to understand conversation format:
  - Conversation start marker → ~1 token
  - Role header (`"user"`) → ~2–3 tokens
  - Actual content → varies
  - Message end marker → ~1–2 tokens
  - **Total overhead: ~5–7 tokens per message**, regardless of content length
- **Practical impact:** For short texts (e.g. `"Hello!"`), the overhead dominates the count. For longer texts, it becomes negligible.

### 2. **Model Tiers**
| Model  | Speed    | Quality | Cost    | Best For                         |
|--------|----------|---------|---------|----------------------------------|
| Haiku  | Fastest  | Good    | Lowest  | High-volume, simple tasks        |
| Sonnet | Balanced | Great   | Medium  | General use, most tasks          |
| Opus   | Slowest  | Best    | Highest | Complex reasoning, critical tasks |

**Observed behaviours from live comparison run (April 7, 2026):**
- **Haiku** is consistently the fastest across all task types — even on hard reasoning it responded in ~2.5s
- **Sonnet** was the most token-efficient for factual/concise tasks (35 output tokens vs Haiku's 39 and Opus's 47)
- **Opus** over-delivers even on simple tasks — e.g. it added a title and markdown formatting to a haiku poem, used 33 tokens vs Haiku's 23, and took 3× longer (3.05s vs 1.05s)
- On the **reasoning task**, both Haiku and Sonnet hit the 300-token ceiling (response cut off); Opus stayed at 292, suggesting slightly more structured reasoning within the limit
- Input token counts are **identical across all models** for the same prompt — tokenisation is consistent

### 3. **max_tokens Behaviour**
- **Learning:** `max_tokens` is a hard ceiling, not a target
- **Impact:** Setting it too low truncates responses mid-sentence
- **Best practice:** Set generously and let the model decide the natural stopping point

### 4. **Cost Awareness**
- **Learning:** Output tokens are 3-5× more expensive than input tokens
- **Optimisation:** Shorter, precise prompts reduce input cost
- **Routing:** Route simple tasks to Haiku to cut costs by 90%+ vs. Opus

### 5. **Usage Metadata**
- **Learning:** Every API response includes `usage.input_tokens` and `usage.output_tokens`
- **Application:** Log this data to track spend and optimise prompts over time

## 🛠️ Technical Implementation Details

### Enhanced `call_llm()` Return Value
```python
{
    "text": "...",
    "input_tokens": 42,
    "output_tokens": 87,
    "total_tokens": 129,
    "model": "claude-sonnet-4-5-20250...",
    "latency_s": 1.23,
}
```

### `count_tokens()` Using the Dedicated Endpoint
```python
result = client.messages.count_tokens(
    model=model,
    messages=[{"role": "user", "content": text}],
)
return result.input_tokens
```

## 📊 Observations

### Token Counting Results:
- `"Hello!"` → **9 tokens** (6 chars) — not ~2, because the API wraps the text in a full message payload adding ~7 structural tokens
- Simple English sentence → ~1 token per 4 chars (for content only, excluding overhead)
- Python `fibonacci` snippet → ~1 token per 3 chars (code is denser)
- Repeated `"A" * 500` → ~125 tokens (exactly 4 chars/token, overhead becomes negligible at scale)

### Model Comparison Results (Live Run, April 7, 2026):

**Factual — "Explain what a neural network is in one sentence"**
| Model  | In Tok | Out Tok | Latency |
|--------|--------|---------|---------|
| Haiku  | 18     | 39      | 1.11s   |
| Sonnet | 18     | 35      | 1.92s   |
| Opus   | 18     | 47      | 1.45s   |
→ Sonnet most concise; Haiku fastest; Opus most verbose

**Creative — "Write a haiku about machine learning"**
| Model  | In Tok | Out Tok | Latency |
|--------|--------|---------|---------|
| Haiku  | 15     | 23      | 1.05s   |
| Sonnet | 15     | 21      | 1.40s   |
| Opus   | 15     | 33      | 3.05s   |
→ Opus added a title + markdown header, inflating token count and latency

**Reasoning — Snail wall problem (10 m wall, max_tokens=300)**
| Model  | In Tok | Out Tok      | Latency |
|--------|--------|--------------|---------|
| Haiku  | 50     | 300 (capped) | 2.55s   |
| Sonnet | 50     | 300 (capped) | 4.71s   |
| Opus   | 50     | 292          | 5.39s   |
→ Haiku & Sonnet hit the token ceiling (response cut off); Opus fit reasoning within limit

## 🚀 Future Enhancements

1. **Streaming Responses:** Show tokens as they arrive
2. **Dynamic Cost Tracking:** Accumulate spend across a session
3. **Prompt Caching:** Explore Anthropic's cache-control headers to reduce costs
4. **Tiktoken Comparison:** Compare Anthropic tokenisation with OpenAI's tiktoken

## 📈 Success Metrics

- **Functions Implemented:** `call_llm`, `count_tokens`, `compare_models` + 4 test functions
- **Models Covered:** Haiku, Sonnet, Opus
- **Cost Workloads Modelled:** 3 representative scenarios
- **Menu Options:** 6

## 🎯 Day 3 Objectives

✅ **Token Counting:** Understand and measure tokens  
✅ **Model Comparison:** Know when to use each tier  
✅ **max_tokens:** Understand truncation behaviour  
✅ **Cost Estimation:** Quantify API spend before scaling  
✅ **Usage Metadata:** Log and interpret token usage from responses  

---

**Development Period:** April 7, 2026  
**Status:** ✅ Complete  
**Next Stage:** Day 4 – Reliable API Calls (retry logic, timeouts, structured logging)

