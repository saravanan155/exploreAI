# 📅 Day-by-Day Breakdown — exploreAI
> Starting from Day 5 (today). Each day: what to watch/read → what code to generate → what to experiment with.
> Folder structure matches your README plan exactly.

---

## ✅ WEEK 1 RECAP (Days 1–4) — Done
| Day | Topic | Status |
|-----|-------|--------|
| 1 | Basic Claude API connection | ✅ |
| 2 | Temperature, context limits, failure modes | ✅ |
| 3 | Token counting, model tiers, cost estimation | ✅ |
| 4 | Retry logic, jitter, timeouts, structured logging | ✅ |

---

## 📦 WEEK 2 — Prompting, Vision & Interfaces (Days 5–12)

---

### Day 5 — Prompt Engineering Part 1
**Folder:** `prompt_engineering/`
**Resource:** https://www.promptingguide.ai/techniques/cot (Chain-of-Thought section onwards)

**What to read/watch first (~45 min):**
- promptingguide.ai → read: Zero-shot, Few-shot, Chain-of-Thought, Self-Consistency

**Code to generate (ask me):**
> "Generate a Python script `prompt_engineering.py` that demonstrates: (1) zero-shot prompting, (2) few-shot prompting with 3 examples, (3) chain-of-thought prompting — all using the Claude API with clearly commented sections. Use a simple task like classifying customer support tickets."

**Experiments to run:**
- Swap zero-shot → few-shot on the same input. Does quality improve?
- Remove the CoT instruction. Does reasoning change?
- Try the same prompts on Haiku vs Sonnet — compare outputs

**learnings.md prompts:**
- What did few-shot examples change vs zero-shot?
- When would you NOT want chain-of-thought?

---

### Day 6 — Prompt Engineering Part 2
**Folder:** `prompt_engineering/` (add to same folder)
**Resource:** https://www.promptingguide.ai/techniques/react + https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking

**What to read/watch first (~45 min):**
- promptingguide.ai → read: ReAct prompting
- Anthropic docs → read: Extended Thinking overview

**Code to generate (ask me):**
> "Add to `prompt_engineering.py`: (1) a ReAct-style prompt that makes Claude reason and act step by step on a multi-step problem, (2) a structured output example using Pydantic that parses Claude's response into a typed Python object, (3) an extended thinking API call with `thinking` budget tokens enabled. Comment every block."

**Experiments to run:**
- Change the `budget_tokens` on extended thinking from 1000 → 5000. Does output depth change?
- Try to get structured output to fail — give it an ambiguous input. How does Pydantic handle it?
- Compare a ReAct prompt vs plain CoT on a math problem

**learnings.md prompts:**
- What's the difference between ReAct and CoT in practice?
- When would structured output with Pydantic be essential in production?

---

### Day 7 — Multimodal (Vision API)
**Folder:** `multi_modal/`
**Resource:** https://docs.anthropic.com/en/docs/build-with-claude/vision

**What to read first (~30 min):**
- Anthropic vision docs — all of it, it's short

**Code to generate (ask me):**
> "Generate a Python script `multi_modal.py` that: (1) sends a local image file to Claude and asks it to describe it, (2) sends a screenshot (PNG) and asks Claude to extract all text from it, (3) sends a PDF page as an image and asks Claude to summarize it. Include base64 encoding, proper media_type handling, and comments on token cost implications of images."

**Experiments to run:**
- Send a screenshot of your code and ask Claude "what does this code do?"
- Send a chart/graph image and ask for data extraction
- Try sending a very low-res image — does quality degrade gracefully?

**learnings.md prompts:**
- How does image token cost compare to text token cost?
- What use cases in your team workspace app could benefit from vision?

---

### Day 8 — FastAPI Backend + Streaming
**Folder:** `chatbot_backend/`
**Resource:** https://fastapi.tiangolo.com/tutorial/ (just Intro + First Steps + Path Parameters)

**What to read first (~30 min):**
- FastAPI docs: Intro, First Steps, Request Body sections only

**Code to generate (ask me):**
> "Generate a FastAPI app `main.py` with: (1) a POST `/chat` endpoint that takes a message and returns a Claude response, (2) a POST `/chat/stream` endpoint that streams Claude's response using Server-Sent Events, (3) basic request/response Pydantic models, (4) CORS middleware enabled. Add comments explaining why streaming matters for LLM UX."

**Experiments to run:**
- Hit `/chat/stream` with curl and watch tokens arrive in real time
- Add a `model` parameter to the request so the caller can choose Haiku vs Sonnet
- Time a streaming vs non-streaming response — feel the difference

**learnings.md prompts:**
- Why does streaming matter for perceived performance even if total time is the same?
- What would break if you deployed this without CORS middleware?

---

### Day 9 — Multi-turn Memory + Auth
**Folder:** `chatbot_backend/` (extend Day 8)
**Resource:** https://docs.anthropic.com/en/docs/build-with-claude/memory-and-context

**What to read first (~30 min):**
- Anthropic docs on memory and context management

**Code to generate (ask me):**
> "Extend the FastAPI app from Day 8: (1) add an in-memory conversation store keyed by session_id so multi-turn context is maintained, (2) add a context window budget — trim oldest messages when approaching token limit, (3) add a simple API key header check (X-API-Key) as auth middleware, (4) add per-session rate limiting (max 10 requests/minute). Comment why context trimming strategy matters."

**Experiments to run:**
- Have a 10-turn conversation — does the bot remember early turns?
- Deliberately exceed the context budget — see how trimming affects coherence
- Hit the rate limit — what HTTP status do you get back?

**learnings.md prompts:**
- What's the tradeoff between trimming oldest messages vs summarizing them?
- How would you scale the session store beyond in-memory for production?

---

### Day 10 — Async, Timeouts & Resilience
**Folder:** `chatbot_backend/` (extend)
**Resource:** Review your `reliable_api_calls/` from Day 4 — apply same patterns to async

**What to read first (~20 min):**
- Re-read your Day 4 `LEARNINGS.md` — you're now applying those patterns to a server context

**Code to generate (ask me):**
> "Refactor the FastAPI chatbot to be fully async: (1) use `anthropic.AsyncAnthropic` client, (2) add connect vs read timeout handling separately, (3) add async retry with jitter on 429/529 errors, (4) add a circuit breaker — after 5 consecutive failures, return a fallback response without hitting the API for 30 seconds. Comment how this differs from synchronous retry logic."

**Experiments to run:**
- Simulate a timeout by setting connect timeout to 0.001s — what happens?
- Trigger the circuit breaker manually — does the fallback respond instantly?
- Compare async vs sync response time under simulated concurrent requests

**learnings.md prompts:**
- Why is `asyncio.sleep` used instead of `time.sleep` in async retry?
- When would a circuit breaker cause more problems than it solves?

---

### Day 11 — React Frontend + Streaming UI
**Folder:** `chatbot_frontend/`
**Resource:** https://react.dev/learn (just Thinking in React section)

**What to read first (~20 min):**
- React docs: "Thinking in React" page only

**Code to generate (ask me):**
> "Generate a single React component `ChatApp.jsx` that: (1) renders a chat UI with message bubbles (user on right, assistant on left), (2) streams tokens from the FastAPI `/chat/stream` endpoint and displays them in real time as they arrive, (3) maintains conversation history in state, (4) shows a typing indicator while streaming, (5) handles errors gracefully. Use plain CSS, no external UI libraries."

**Experiments to run:**
- Connect it to your Day 8/9/10 FastAPI backend
- Watch tokens render in real time — notice the UX difference vs waiting for full response
- Deliberately break the stream URL — how does the error state render?

**learnings.md prompts:**
- How does the browser's `EventSource` or `fetch` with `ReadableStream` handle reconnects?
- What would you add to make this production-ready for real users?

---

### Day 12 — Polish + Integration Test
**Folder:** `chatbot_frontend/` + `chatbot_backend/`

**No new concepts today — this is integration day.**

**Code to generate (ask me):**
> "Write a Python integration test script `test_chatbot.py` using `httpx` that: (1) tests the full conversation loop — sends 5 messages and validates responses aren't empty, (2) tests rate limiting fires after 10 requests/minute, (3) tests the streaming endpoint and validates tokens arrive incrementally, (4) tests auth rejection when X-API-Key is missing."

**Experiments to run:**
- Run the full test suite against your local server
- Fix anything that breaks
- Do a full end-to-end demo: React UI → FastAPI → Claude → streamed back

**learnings.md prompts:**
- What parts were hardest to integrate? Why?
- What would you do differently if starting over?

---

## 📦 WEEK 3 — Embeddings & RAG (Days 13–16)

---

### Day 13 — Embeddings & Vector Similarity
**Folder:** `embeddings/`
**Resource:** https://www.promptingguide.ai/research/rag (intro section) + https://docs.anthropic.com/en/docs/build-with-claude/embeddings

**What to read first (~45 min):**
- Anthropic embeddings docs
- Promptingguide.ai RAG intro section

**Code to generate (ask me):**
> "Generate `embeddings.py` that: (1) calls an embedding model (use `voyage-3` via Anthropic or `text-embedding-3-small` via OpenAI) to embed 10 short sentences, (2) computes cosine similarity between all pairs and prints the most/least similar, (3) visualizes the similarity matrix as a simple ASCII heatmap, (4) demonstrates why 'bank' (river) and 'bank' (finance) embed differently with context. Comment what cosine similarity actually measures."

**Experiments to run:**
- Embed synonyms — do they land near each other?
- Embed a question and its answer — are they close?
- Embed your name and a random word — what's the similarity?

**learnings.md prompts:**
- What does it mean geometrically when two embeddings have cosine similarity of 0.95?
- Why can't you just use string matching instead of embeddings?

---

### Day 14 — Vector DB + Basic RAG
**Folder:** `llm_with_rag/`
**Resource:** https://learn.deeplearning.ai/courses/retrieval-augmented-generation/information (Modules 1 & 2)

**What to watch first (~60 min):**
- DeepLearning.AI RAG Course — complete Modules 1 and 2 (build your first RAG + information retrieval techniques)

**Code to generate (ask me):**
> "Generate `rag_basic.py` that: (1) loads 5 text documents from a local folder, (2) chunks them with a fixed 500-token window and 50-token overlap, (3) embeds all chunks and stores them in Qdrant (local in-memory mode), (4) takes a user query, embeds it, retrieves top-3 chunks by cosine similarity, (5) passes retrieved chunks + query to Claude to generate a grounded answer, (6) prints which source chunks were used. Comment why chunk overlap matters."

**Experiments to run:**
- Ask a question whose answer spans two chunks — does retrieval catch both?
- Remove chunk overlap — does answer quality change?
- Ask a question the documents don't answer — does the model hallucinate or say "I don't know"?

**learnings.md prompts:**
- What does "grounded" mean in the context of RAG vs a plain LLM response?
- Why is chunk size a tradeoff, not a "bigger is better" decision?

---

### Day 15 — Advanced Retrieval
**Folder:** `llm_with_rag/` (extend)
**Resource:** https://learn.deeplearning.ai/courses/retrieval-augmented-generation/information (Modules 3 & 4)

**What to watch first (~60 min):**
- DeepLearning.AI RAG Course — complete Modules 3 and 4 (vector DB scaling, chunking, reranking)

**Code to generate (ask me):**
> "Extend `rag_basic.py` into `rag_advanced.py`: (1) add BM25 keyword search alongside semantic search (use `rank_bm25` library), (2) implement Reciprocal Rank Fusion to merge BM25 + semantic results, (3) add a reranker step — use Claude to score each retrieved chunk for relevance before passing to generation, (4) add multi-query retrieval — generate 3 query variants from the original question and union results. Comment the tradeoff between each strategy."

**Experiments to run:**
- Compare plain semantic vs hybrid (BM25 + semantic) on a keyword-heavy query
- Skip the reranker — does answer quality visibly drop?
- Try multi-query on a vague question — does it retrieve more relevant chunks?

**learnings.md prompts:**
- When would BM25 outperform semantic search?
- Is reranking always worth the extra API call cost?

---

### Day 16 — RAG with LangChain
**Folder:** `llm_with_rag/` (extend)
**Resource:** https://python.langchain.com/docs/concepts/rag/

**What to read first (~30 min):**
- LangChain RAG conceptual guide — read the full page

**Code to generate (ask me):**
> "Rewrite the Day 14 basic RAG pipeline in `rag_langchain.py` using LangChain LCEL: (1) use `RecursiveCharacterTextSplitter` for chunking, (2) `QdrantVectorStore` for storage, (3) `ConversationalRetrievalChain` for multi-turn RAG, (4) add source document citation in the response. Then add a side-by-side comparison comment — for each LangChain abstraction, note what raw code it replaced from Day 14."

**Experiments to run:**
- Ask the same 5 questions to your Day 14 raw RAG vs this LangChain RAG — same results?
- Deliberately give it a multi-turn conversation — does context carry over?
- Look at what LCEL actually generates under the hood using `.get_prompts()`

**learnings.md prompts:**
- What did LangChain make easier? What did it hide that you now understand because you did Day 14 first?
- Would you use raw RAG or LangChain in your team workspace app? Why?

---

## 📦 WEEK 4 — Tools, Agents & MCP (Days 17–21)

---

### Day 17 — Function Calling & Tool Use
**Folder:** `tool_calling/`
**Resource:** https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview

**What to read first (~45 min):**
- Anthropic tool use docs — full overview page

**Code to generate (ask me):**
> "Generate `tool_calling.py` that: (1) defines 3 tools — `get_weather(city)`, `search_jira(query)` (mock), `create_jira_story(title, description)` (mock), (2) passes them to Claude as tool definitions, (3) runs a loop that handles tool_use responses — calls the mock function and feeds results back to Claude, (4) continues until Claude gives a final text response. Comment the full request/response cycle for each tool call."

**Experiments to run:**
- Ask Claude a question that requires chaining 2 tools
- Ask a question where no tool is needed — does Claude skip tool use correctly?
- Add a tool that intentionally returns an error — how does Claude handle it?

**learnings.md prompts:**
- What's the difference between a tool call and a function call in the API response?
- How would you handle a tool that takes 10 seconds to respond?

---

### Day 18 — MCP (Model Context Protocol)
**Folder:** `tool_calling/` (extend)
**Resource:** https://modelcontextprotocol.io/introduction + https://modelcontextprotocol.io/docs/concepts/architecture

**What to read first (~45 min):**
- MCP docs: Introduction + Core Architecture + Tools primitive page

**Code to generate (ask me):**
> "Generate a minimal MCP server `mcp_server.py` using the `mcp` Python SDK that: (1) exposes a `search_documents` tool that queries a local Qdrant collection (reuse from Day 14), (2) exposes a `get_sprint_context` resource that returns mock sprint data as JSON, (3) runs as a local stdio server. Then write `mcp_client.py` that connects to it and calls both the tool and resource via Claude."

**Experiments to run:**
- Add a second tool to the MCP server without changing the client — does Claude discover it automatically?
- Compare calling Qdrant directly (Day 14) vs through MCP — what's different from Claude's perspective?

**learnings.md prompts:**
- What problem does MCP solve that plain function calling doesn't?
- How would you use MCP in your team workspace app?

---

### Day 19 — ReAct Agents
**Folder:** `agents/`
**Resource:** https://academy.langchain.com/courses/intro-to-langgraph (Lessons 1–3)

**What to watch first (~60 min):**
- LangChain Academy: Intro to LangGraph — complete first 3 lessons (graph basics, nodes, edges, state)

**Code to generate (ask me):**
> "Generate `react_agent.py` using LangGraph that: (1) implements a ReAct agent with a Thought → Action → Observation loop, (2) gives it 3 tools: web_search (mock), calculator, and jira_lookup (mock), (3) uses LangGraph StateGraph with MessagesState, (4) adds a conditional edge that routes to END when Claude produces a final answer vs loops back when it calls a tool. Visualize the graph structure with `draw_mermaid_png`. Comment every node and edge."

**Experiments to run:**
- Give it a multi-step problem that needs 3 tool calls
- Set a max iteration limit — what happens when it's reached?
- Watch the Thought/Action/Observation trace — where does reasoning happen?

**learnings.md prompts:**
- How is LangGraph's StateGraph different from just chaining function calls?
- What would break if you removed the conditional edge?

---

### Day 20 — Multi-Agent Systems
**Folder:** `agents/` (extend)
**Resource:** https://academy.langchain.com/courses/intro-to-langgraph (Lessons 4–6)

**What to watch first (~60 min):**
- LangChain Academy: continue from Lesson 4 (multi-agent, memory, human-in-the-loop)

**Code to generate (ask me):**
> "Build `multi_agent.py` using LangGraph with 3 specialized agents: (1) `researcher_agent` — retrieves context from Qdrant RAG, (2) `writer_agent` — drafts Jira stories from retrieved context, (3) `reviewer_agent` — critiques the draft and sends back for revision if quality score < 8/10. Wire them as a LangGraph supervisor pattern. Add human-in-the-loop at the review step — pause and ask for approval before finalizing."

**Experiments to run:**
- Force the reviewer to reject the first draft — watch the revision loop
- Skip the researcher — does the writer produce worse stories?
- Trigger the human-in-the-loop — approve, reject, and see both paths

**learnings.md prompts:**
- What's the supervisor pattern and when would you use it vs a peer pattern?
- How does human-in-the-loop change the production deployment model?

---

### Day 21 — Integration + Polish
**Folder:** `agents/`

**No new concepts — this is consolidation day.**

**Code to generate (ask me):**
> "Create `jira_agent_app.py` that combines everything from Days 17–20 into one cohesive agent: MCP server for tools, RAG for context retrieval, LangGraph for orchestration, FastAPI endpoint to trigger it via HTTP, and LangSmith tracing enabled via environment variable. Add a README for the `agents/` folder documenting the architecture with a text diagram."

**Experiments to run:**
- Run an end-to-end flow: HTTP request → agent → RAG → MCP tool → Jira story output
- Enable LangSmith tracing and look at the full trace in the dashboard
- Time the full flow — where are the bottlenecks?

**learnings.md prompts:**
- What surprised you about how all these pieces fit together?
- What would you refactor first if this were going to production?

---

## 📦 WEEK 5 — Safety, Evals & Cost (Days 22–25)

---

### Day 22 — Safety & Guardrails
**Folder:** `safety_and_guardrails/`
**Resource:** https://docs.anthropic.com/en/docs/build-with-claude/guardrails

**What to read first (~30 min):**
- Anthropic guardrails docs

**Code to generate (ask me):**
> "Generate `guardrails.py` that demonstrates: (1) prompt injection defence — detect and block inputs containing instruction overrides, (2) output validation — parse Claude's response and reject if it contains PII patterns (email, SSN, phone), (3) a content filter that uses Claude itself to classify whether an input is safe before passing to the main model, (4) a fallback response handler when safety checks fail. Comment what each guard catches and what it misses."

---

### Day 23 — LLM Evals
**Folder:** `evals_and_observability/`
**Resource:** https://www.evidentlyai.com/llm-course (first 3 modules)

**What to watch first (~60 min):**
- Evidently AI LLM Evals Course — complete first 3 modules

**Code to generate (ask me):**
> "Generate `evals.py` that: (1) creates a golden dataset of 10 question/expected-answer pairs for your RAG pipeline, (2) runs each question through your Day 15 RAG and collects actual answers, (3) uses RAGAS to score faithfulness, answer_relevancy, and context_precision for each, (4) outputs a summary table and flags any score below 0.7 as failing. Comment what each RAGAS metric actually measures."

---

### Day 24 — Observability with LangSmith
**Folder:** `evals_and_observability/` (extend)
**Resource:** https://docs.smith.langchain.com/ (Quickstart)

**Code to generate (ask me):**
> "Add LangSmith tracing to your Day 21 agent app: (1) instrument every LangGraph node with LangSmith trace decorators, (2) add custom metadata tags (session_id, user_id, sprint_id) to each trace, (3) create a LangSmith dataset from your Day 23 golden set and run it as an automated evaluation, (4) add a simple dashboard print that shows pass/fail per test case. Comment what you can debug with LangSmith that you couldn't without it."

---

### Day 25 — Cost Optimization
**Folder:** `cost_optimization/`
**Resource:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

**What to read first (~30 min):**
- Anthropic prompt caching docs

**Code to generate (ask me):**
> "Generate `cost_optimization.py` that demonstrates: (1) prompt caching with `cache_control` — cache a large system prompt and measure token savings across 10 calls, (2) semantic caching — embed incoming queries and return cached responses for queries with cosine similarity > 0.95, (3) model routing — classify query complexity and route simple queries to Haiku, complex to Sonnet, (4) batch API usage for offline evaluation runs. Print a cost comparison table for each optimization."

---

## 📦 WEEK 6 — Fullstack App + Deploy (Days 26–30)

---

### Days 26–28 — Full Stack App
**Folder:** `fullstack_app/`

**Code to generate (ask me on Day 26):**
> "Scaffold a fullstack app `fullstack_app/` that integrates: FastAPI backend (Days 8–10), React frontend (Days 11–12), LangGraph agent (Day 21), RAG pipeline (Days 14–15), guardrails (Day 22), LangSmith tracing (Day 24), and cost optimization (Day 25). Generate a `docker-compose.yml` that runs FastAPI + Qdrant together. Generate a top-level architecture README with a component diagram."

Use Days 27–28 to wire components together, fix integration issues, and write integration tests.

---

### Day 29 — Deployment
**Folder:** `deployment/`
**Resource:** https://docs.docker.com/get-started/ (just Part 1–2)

**Code to generate (ask me):**
> "Generate: (1) a production `Dockerfile` for the FastAPI app with multi-stage build, (2) a `docker-compose.prod.yml` with Qdrant, FastAPI, and environment variable injection from `.env`, (3) a GitHub Actions workflow `.github/workflows/deploy.yml` that runs tests on PR and builds the Docker image on merge to main, (4) a secrets management guide `SECRETS.md` explaining what should never be in the repo."

---

### Day 30+ — Fine-Tuning
**Folder:** `fine_tuning/`
**Resource:** https://github.com/unslothai/unsloth (Llama 3.2 3B Colab notebook)

**Code to generate (ask me on Day 30):**
> "Generate `fine_tuning/prepare_dataset.py` that: (1) loads your existing Jira story examples (input/output pairs), (2) formats them as instruction-following JSONL for supervised fine-tuning, (3) splits into 80/20 train/val, (4) validates format against the Unsloth expected schema, (5) prints dataset statistics. Then I'll run the actual QLoRA training in Unsloth on Google Colab."

---

## 📋 Quick Reference — Daily Routine

```
1. Open today's resource (watch/read) — 30–60 min
2. Come to Claude and ask for the day's code — use the prompt above verbatim
3. Run the code, break it, fix it — 45–60 min
4. Ask Claude follow-up questions on anything that confused you
5. Fill in learnings.md before closing your laptop
6. git commit with message: "Day X: [topic]"
```

---

## 🗂️ Folder Structure (Full Plan)

```
exploreAI/
├── basicllm/                    # Day 1  ✅
├── llm_intuition/               # Day 2  ✅
├── tokens_and_models/           # Day 3  ✅
├── reliable_api_calls/          # Day 4  ✅
├── prompt_engineering/          # Day 5–6
├── multi_modal/                 # Day 7
├── chatbot_backend/             # Day 8–10
├── chatbot_frontend/            # Day 11–12
├── embeddings/                  # Day 13
├── llm_with_rag/                # Day 14–16
├── tool_calling/                # Day 17–18
├── agents/                      # Day 19–21
├── safety_and_guardrails/       # Day 22
├── evals_and_observability/     # Day 23–24
├── cost_optimization/           # Day 25
├── fullstack_app/               # Day 26–28
├── deployment/                  # Day 29
├── fine_tuning/                 # Day 30+
├── CHECKLIST.md
├── DAY_BY_DAY.md                # This file
└── README.md
```
