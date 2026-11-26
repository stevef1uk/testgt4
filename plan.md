# Implementation plan: ai-trading-assistant

Scope: Phase 6 (AI Trading Assistant). Covers only the nine paths in this phase's required_files. Depends on portfolio-visualisation-trading (portfolio engine, trade route, and watchlist already delivered).

## Bead map

### te-hdu: finally/backend/app/llm/__init__.py
- Scope: package marker for the llm subpackage; re-exports the public entry points used by routes_chat.py.
- Architecture: Backend LLM package, ai-trading-assistant section of architecture.md.
- Interfaces: re-exports `parse_llm_reply` from parser.py and the chat service entry point from chat_service.py.
- Depends on: te-wqs (client.py), te-duq (prompts.py), te-p35 (parser.py), te-3dr (chat_service.py).
- Consumed by: te-13d (routes_chat.py).
- Acceptance: importing `app.llm` succeeds with LLM_MOCK=true and no OPENROUTER_API_KEY set; no network calls at import time.
- Verify: cd finally/backend && LLM_MOCK=true uv run python -c "import app.llm"

### te-wqs: finally/backend/app/llm/client.py
- Scope: LLM client wrapper. LiteLLM to OpenRouter (Cerebras inference, model openrouter/openai/gpt-oss-120b), with a direct HTTP fallback to OpenRouter. When LLM_MOCK=true, returns deterministic mock responses without network access.
- Architecture: SPEC Section 9 and architecture.md ai-trading-assistant requirement.
- Interfaces: a single async call that takes a system prompt, portfolio context, history, and user message, and returns the raw model text.
- Depends on: te-duq (prompts.py) for message assembly input shape.
- Consumed by: te-3dr (chat_service.py).
- Acceptance: with LLM_MOCK=true, identical inputs return identical raw text; with a missing key and LLM_MOCK unset, the error is raised and surfaced, not swallowed.
- Verify: cd finally/backend && LLM_MOCK=true uv run pytest tests/test_llm.py -q

### te-duq: finally/backend/app/llm/prompts.py
- Scope: system prompt ("FinAlly, an AI trading assistant") and market context construction.
- Architecture: SPEC Section 9 live price context requirement.
- Interfaces: a function that builds the context string from cash, positions, watchlist, and live prices, rendering each watchlist symbol as `AAPL ($190.50)`.
- Depends on: none within this phase (inputs come from the portfolio and market cache already delivered).
- Consumed by: te-wqs (client.py), te-3dr (chat_service.py).
- Acceptance: every watchlist ticker appears in the context with its live price in the `TICKER ($price)` form; the system prompt requires a JSON object matching the reply/trade schema.
- Verify: cd finally/backend && LLM_MOCK=true uv run pytest tests/test_llm.py -q

### te-p35: finally/backend/app/llm/parser.py
- Scope: resilient multi-key parser. Exposes `parse_llm_reply(raw: str)`.
- Architecture: SPEC Section 9 Resilient Parser; module ownership table in architecture.md.
- Interfaces: `parse_llm_reply(raw: str)` returns the reply text, an optional trade `{ticker, side, quantity}`, and any action payload.
- Depends on: none (pure function, no network).
- Consumed by: te-3dr (chat_service.py).
- Acceptance: reads the keys `reply`, `response`, `message`, `content`, `action`, `error`, `suggestion`; an action object such as `{"action":"buy","ticker":"AAPL","quantity":2}` is converted to a trade and a human-readable confirmation string such as `Order BUY 2 AAPL: executed.`; malformed input returns a safe fallback text and never raw JSON brackets.
- Verify: cd finally/backend && LLM_MOCK=true uv run pytest tests/test_llm.py -q

### te-3dr: finally/backend/app/llm/chat_service.py
- Scope: orchestrates one chat turn: load portfolio context and history, build prompt, call the client, parse, auto-execute trades and watchlist changes through the existing portfolio engine, persist to chat_messages, and return the complete response.
- Architecture: SPEC Section 9 How It Works steps 1 to 8.
- Interfaces: a service function that takes the user message and returns `{message, actions}`.
- Depends on: te-wqs (client.py), te-duq (prompts.py), te-p35 (parser.py).
- Consumed by: te-13d (routes_chat.py).
- Acceptance: a buy request in mock mode executes through the portfolio engine (cash decreases, position appears); a trade that fails validation is reported in the reply, not silently dropped; the user and assistant rows are written to chat_messages with actions JSON for the assistant row.
- Verify: cd finally/backend && LLM_MOCK=true uv run pytest tests/test_llm.py -q

### te-13d: finally/backend/app/api/routes_chat.py
- Scope: POST /api/chat route, a thin wrapper around chat_service.
- Architecture: SPEC Section 8 Chat row; architecture.md HTTP table.
- Interfaces: POST /api/chat with request `{message}` and response `{message, actions}`, matching SPEC Section 8 verbatim (no aliases).
- Depends on: te-3dr (chat_service.py), te-hdu (package __init__).
- Consumed by: finally/backend/app/main.py router registration (owned by project-foundation).
- Acceptance: POST /api/chat with a valid message returns 200 and a non-empty `message` string; response never contains raw JSON brackets as the message text.
- Verify: cd finally/backend && LLM_MOCK=true uv run pytest tests/test_llm.py -q

### te-la7: finally/backend/tests/test_llm.py
- Scope: pytest suite for the LLM package.
- Architecture: architecture.md Unit tests, test_llm.py entry: parser variants, malformed input, chat trade validation, mock determinism.
- Interfaces: exercises parse_llm_reply, the prompt builder, the chat service, and the mock client through public functions only.
- Depends on: te-p35, te-duq, te-wqs, te-3dr, te-13d.
- Consumed by: phase QA gate.
- Acceptance: asserts returned values, not status codes alone. Covers: each reply key variant, the action-to-confirmation conversion, malformed JSON fallback, a buy that executes and updates cash, an oversell that is rejected, and identical mock output for identical input.
- Verify: cd finally/backend && LLM_MOCK=true uv run pytest tests/test_llm.py -q

### te-0o9: finally/frontend/components/ChatAssistant.tsx
- Scope: docked chat sidebar with message bubbles, thinking indicator, input, Send button, and trade fill badges.
- Architecture: SPEC Section 10 item 6; architecture.md ai-trading-assistant requirement.
- Interfaces: `aria-label="Chat assistant"` on the container, `aria-label="Chat message"` on the input, a Send button, loading text `Copilot is thinking...`, and badges rendered as `✓ Trade Fill: SIDE QTY TICKER`.
- Depends on: POST /api/chat from te-13d.
- Consumed by: finally/frontend/app/page.tsx (amended in application-polish).
- Acceptance: Enter key and Send button both submit; the thread auto-scrolls to the newest message; a successful trade triggers a portfolio refresh callback; any stringified JSON reply is unwrapped to plain text before rendering.
- Verify: cd finally/frontend && npm run build

### te-uav: finally/frontend/components/ChatAssistant.test.tsx
- Scope: component tests for ChatAssistant.
- Architecture: architecture.md Unit tests, ChatAssistant.test.tsx entry: bubble rendering, thinking state, JSON unwrapping.
- Interfaces: renders ChatAssistant with a mocked chat endpoint.
- Depends on: te-0o9.
- Consumed by: phase QA gate.
- Acceptance: user and assistant bubbles render their text; the thinking indicator is visible while the request is pending; a stringified JSON reply such as `{"reply":"Hi"}` renders as `Hi` with no braces visible.
- Verify: cd finally/frontend && npm run build
