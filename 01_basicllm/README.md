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

## 🔍 Understanding the API Response

When you call `client.messages.create()`, the Anthropic API returns a **Message object** with detailed information about the response. Here's what you get back:

### Full Response Structure

```python
Message(
    id='msg_01P2Dwnjd3t2sGvk9fJGBssy',
    content=[TextBlock(text='Machine learning is...', type='text')],
    model='claude-sonnet-4-6-20250514',
    role='assistant',
    stop_reason='end_turn',
    usage=Usage(
        input_tokens=45,
        output_tokens=128,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0
    )
)
```

### Breaking Down Each Field

| Field | Example Value | What It Means | Possible Values |
|---|---|---|---|
| **id** | `msg_01P2Dwnjd3t2sGvk9fJGBssy` | Unique identifier for this response | Any unique string assigned by Claude |
| **content[0].text** | `Machine learning is...` | The actual response from Claude | Any text Claude generates based on your prompt |
| **content[0].type** | `text` | Type of content block | `'text'` (most common), `'tool_use'` (when using function calling) |
| **model** | `claude-sonnet-4-6-20250514` | Exact model version used | `claude-haiku-4-5-...`, `claude-sonnet-4-6-...`, `claude-opus-4-5-...` |
| **role** | `assistant` | Who generated this message | Always `'assistant'` for Claude responses |
| **stop_reason** | `end_turn` | Why the response ended | `'end_turn'` (natural), `'max_tokens'` (hit limit), `'tool_use'` (called a function) |

### Usage Metrics (Important for Cost)

```python
usage=Usage(
    input_tokens=45,        # Tokens in YOUR prompt
    output_tokens=128,      # Tokens in Claude's response
    cache_creation_input_tokens=0,    # Tokens written to cache (if enabled)
    cache_read_input_tokens=0         # Cached tokens reused (if available)
)
```

**What Each Means:**
- **input_tokens** = Cost factor: `input_tokens / 1,000,000 × $3.00` (for Sonnet)
  - Includes your question, system prompt, and message history
  - Example: 45 tokens → $0.000135
  
- **output_tokens** = Cost factor: `output_tokens / 1,000,000 × $15.00` (for Sonnet)
  - Claude's response text
  - 5× more expensive than input tokens
  - Example: 128 tokens → $0.00192

- **cache_creation_input_tokens** = How many tokens were stored in the cache
  - Only used if you enable prompt caching (Day 25 feature)
  - Saves money on repeated prompts (90% discount)

- **cache_read_input_tokens** = How many cached tokens were reused
  - Only set when previous calls set up cache
  - Reduces cost significantly on follow-up requests

### Total Cost Example

```
Input:  45 tokens   × $3.00 / 1M = $0.000135
Output: 128 tokens  × $15.00 / 1M = $0.00192
───────────────────────────────────────────
Total:                              $0.002055  (about 0.2 cents)
```

### What to Extract from the Response

In `llm_basic.py`, we extract only what we need:

```python
response = client.messages.create(...)  # Full Message object

# Extract just the text response
text = response.content[0].text          # "Machine learning is..."

# Track tokens for cost monitoring
input_tokens = response.usage.input_tokens      # 45
output_tokens = response.usage.output_tokens    # 128
total_tokens = input_tokens + output_tokens     # 173

# Get metadata
model_used = response.model                     # "claude-sonnet-4-6-20250514"
stop_reason = response.stop_reason              # "end_turn"
```

### Handling Different Stop Reasons

```python
if response.stop_reason == "end_turn":
    # Normal, Claude finished naturally ✅
    return response.content[0].text

elif response.stop_reason == "max_tokens":
    # Claude hit the token limit — response was cut off ⚠️
    # This means the response is incomplete
    return response.content[0].text  # Partial response

elif response.stop_reason == "tool_use":
    # Claude decided to call a function (Day 14–15 feature)
    # response.content[0] will be a ToolUse object, not TextBlock
    pass
```

### Common Error Scenarios

**Scenario 1: Empty Response**
```python
if not response.content or len(response.content) == 0:
    raise ValueError("Claude returned empty response")
```

**Scenario 2: High Token Count (means higher cost)**
```python
if response.usage.output_tokens > 1000:
    print(f"⚠️ High output: {response.usage.output_tokens} tokens")
    # This response costs more than expected
```

**Scenario 3: Model Not Available**
```python
# If you request "claude-opus-4-5" but it's not available
# The API will return a 404 error instead of a Message object
```

## ⚠️ Limitations

- Knowledge cutoff: ~February 2026 (based on Claude Sonnet 4.6 training data)
- No real-time data access
- Cannot browse internet or access current APIs
- Responses based solely on training data

---

**Status:** ✅ Ready for use
**Last Updated:** April 6, 2026
