# Prompt Engineering – Development Notes

## 🎯 Day 5–6 Focus: Prompt Engineering
**Goal:** Master prompting strategies — zero-shot, few-shot, and chain-of-thought — and understand cost/accuracy trade-offs
**Started:** April 12, 2026

## 📈 Development Journey

### Building on Day 4 (reliable_api_calls)
- ✅ Copied package structure from `reliable_api_calls/`
- ✅ Simplified `call_llm()` to focus on prompting — added `system_prompt` parameter
- ✅ Set `temperature=0.0` as default for deterministic classification
- ✅ Chose customer support ticket classification as the hands-on task

### Phase 1: Zero-Shot Prompting
- ✅ Wrote `ZERO_SHOT_SYSTEM` — instructions only, no examples
- ✅ Implemented `classify_zero_shot()` using system prompt + user message
- ✅ Built `test_zero_shot()` to classify 5 sample tickets

### Phase 2: Few-Shot Prompting
- ✅ Wrote `FEW_SHOT_SYSTEM` — instructions + 3 labelled examples embedded in system prompt
- ✅ Implemented `classify_few_shot()` with user prompt matching example format
- ✅ Built `test_few_shot()` to classify 5 sample tickets

### Phase 3: Chain-of-Thought Prompting
- ✅ Wrote `COT_SYSTEM` — instructions + category descriptions + step-by-step format
- ✅ Implemented `classify_chain_of_thought()` with response parsing (reasoning + category)
- ✅ Built `test_chain_of_thought()` to classify 5 sample tickets with visible reasoning

### Phase 4: Interactive Interface
- ✅ 6-option menu system
- ✅ Side-by-side comparison mode (all 3 strategies on one ticket)
- ✅ Custom ticket mode with strategy selection
- ✅ Graceful error handling throughout

## 🧠 Key Learnings from Day 5

### 1. **System Prompts vs. User Messages**
- **Learning:** System prompts set the model's role and behaviour for the entire conversation
- **Implementation:** `system` is a top-level API parameter, NOT a message with `role: "system"`
- **Claude API:** `client.messages.create(system="...", messages=[{"role": "user", ...}])`
- **Use for:** Classification rules, output format, personality, constraints

### 2. **Zero-Shot Prompting**
- **What:** Give the model a task with NO examples — rely on pre-trained knowledge
- **Strengths:** Cheapest (fewest input tokens), simplest prompt, no examples to maintain
- **Weaknesses:** Output format may vary, struggles with ambiguous inputs, may not match your exact categories
- **Best for:** Simple, clear-cut tasks where the model's default understanding is sufficient

### 3. **Few-Shot Prompting**
- **What:** Provide 3+ labelled examples in the system prompt so the model sees the pattern
- **Strengths:** Consistent output format, anchors model to your exact categories, better accuracy
- **Weaknesses:** More input tokens per call (examples sent every time), examples may bias the model
- **Best for:** Tasks requiring consistent format and category names
- **Tip:** Choose diverse, representative examples — don't cluster on one category

### 4. **Chain-of-Thought (CoT) Prompting**
- **What:** Ask the model to reason step-by-step before giving the final answer
- **Strengths:** Most accurate on ambiguous inputs, reasoning is visible (debuggable), fewer careless mistakes
- **Weaknesses:** Highest output token count (most expensive), slower, requires response parsing
- **Best for:** Complex or multi-intent tickets where accuracy matters more than speed/cost
- **Trade-off:** You're paying for the model to "think aloud" — more output tokens = higher cost

### 5. **Temperature for Classification**
- **Learning:** Temperature 0.0 gives deterministic output — same input always produces same category
- **When to raise:** Creative writing, brainstorming, or when you want diverse outputs
- **For classification:** Always use 0.0 — you want consistency, not creativity

## 🛠️ Technical Implementation Details

### System Prompt Architecture
```
┌──────────────────────────────────────┐
│  system_prompt                       │  ← Sets role, rules, format
│  (top-level API parameter)           │
├──────────────────────────────────────┤
│  messages: [                         │
│    { role: "user", content: "..." }  │  ← The actual ticket to classify
│  ]                                   │
└──────────────────────────────────────┘
```

### Zero-Shot Prompt Structure
```
System: "You are a classifier. Categories: [A, B, C]. Respond with ONLY the name."
User:   "Classify this ticket: <ticket text>"
```

### Few-Shot Prompt Structure
```
System: "You are a classifier. Categories: [A, B, C].
         Example 1: <input> → A
         Example 2: <input> → B
         Example 3: <input> → C
         Now classify the next ticket."
User:   "Ticket: <ticket text>\nCategory:"
```

### CoT Prompt Structure
```
System: "You are a classifier. Categories with descriptions: [A=..., B=..., C=...].
         Think step-by-step: 1) key words, 2) match intent, 3) classify.
         Format: Reasoning: <...>\nCategory: <...>"
User:   "Classify this ticket: <ticket text>"
```

### `call_llm()` Signature (Day 5 version)
```python
def call_llm(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    model: str = "claude-haiku-4-5",
    temperature: float = 0.0,
    max_tokens: int = 500,
) -> dict:
```

## 📊 Observations

*(To be filled in after running the program)*

### Zero-Shot Results:
- Classification accuracy:
- Tokens per ticket:
- Format consistency:

### Few-Shot Results:
- Classification accuracy:
- Tokens per ticket:
- Format consistency:

### Chain-of-Thought Results:
- Classification accuracy:
- Tokens per ticket:
- Reasoning quality:

### Side-by-Side Comparison:
- Token cost difference:
- Accuracy difference:
- Latency difference:

## 🚀 Day 6 Planned Work

- ⬜ **Extended Thinking API** — Claude's native reasoning mode vs. CoT prompting
- ⬜ **Structured Outputs with Pydantic** — enforce exact JSON schema on responses
- ⬜ **Prompt Versioning** — track and compare prompt iterations over time
- ⬜ **Input Validation** — sanitise and validate user input before sending to the API

## 📈 Success Metrics

- **Prompting Strategies:** Zero-shot, few-shot, chain-of-thought
- **Classification Functions:** `classify_zero_shot`, `classify_few_shot`, `classify_chain_of_thought`
- **Sample Tickets:** 5 across all categories
- **Menu Options:** 6

## 🎯 Day 5 Objectives

✅ **Zero-Shot:** Classify tickets with no examples
✅ **Few-Shot:** Classify tickets with 3 labelled examples
✅ **Chain-of-Thought:** Step-by-step reasoning before classification
✅ **System Prompts:** Use the `system` parameter to guide model behaviour
✅ **Comparison:** Side-by-side token/accuracy/latency comparison of all 3 strategies
✅ **Temperature:** Understand why 0.0 is correct for classification

---

**Development Period:** April 12, 2026
**Status:** 🚧 In Progress
**Next Stage:** Day 6 – Extended thinking API, structured outputs (Pydantic), prompt versioning

