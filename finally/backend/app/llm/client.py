"""LLM client for the FinAlly chat assistant.

Supports an OpenAI-compatible chat completions endpoint (OpenRouter by default)
and a deterministic mock used when ``LLM_MOCK=true``.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Protocol

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-4o-mini"
REQUEST_TIMEOUT_SECONDS = 60


class LLMError(RuntimeError):
    """Raised when the LLM provider call fails."""


class LLMClient(Protocol):
    """Minimal interface used by the chat service."""

    def complete(self, system_prompt: str, user_message: str) -> str:
        """Return the raw text content of the model reply."""
        ...


class MockLLMClient:
    """Deterministic client that returns a valid reply/trade JSON object."""

    def complete(self, system_prompt: str, user_message: str) -> str:
        reply = {
            "message": f"Mock reply to: {user_message[:200]}",
            "trades": [],
            "watchlist_changes": [],
        }
        return json.dumps(reply)


class OpenAICompatibleClient:
    """Calls a chat completions endpoint with a bearer API key."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        if not api_key:
            raise LLMError("API key is required for the live LLM client")
        self._api_key = api_key
        self._model = model
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._timeout = timeout

    def complete(self, system_prompt: str, user_message: str) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }
        request = urllib.request.Request(
            self._url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as exc:
            raise LLMError(f"LLM request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise LLMError("LLM response was not valid JSON") from exc

        try:
            return body["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("LLM response missing message content") from exc


def create_llm_client() -> LLMClient:
    """Build the client from environment: mock when LLM_MOCK=true, else live."""
    if os.getenv("LLM_MOCK", "").lower() == "true":
        return MockLLMClient()
    return OpenAICompatibleClient(
        api_key=os.getenv("OPENROUTER_API_KEY", ""),
        model=os.getenv("LLM_MODEL", DEFAULT_MODEL),
        base_url=os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL),
    )