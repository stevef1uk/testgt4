"""Chat endpoint: forwards a user message to the LLM assistant with live context."""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.llm import ChatService, create_llm_client

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    cash: float = 0.0
    positions: list[dict[str, Any]] = Field(default_factory=list)
    watchlist: list[str] = Field(default_factory=list)
    prices: dict[str, float] = Field(default_factory=dict)


class TradeOut(BaseModel):
    ticker: str
    side: str
    quantity: float


class WatchlistChangeOut(BaseModel):
    ticker: str
    action: str


class ChatResponse(BaseModel):
    message: str
    trades: list[TradeOut]
    watchlist_changes: list[WatchlistChangeOut]


_service: ChatService | None = None


def get_chat_service() -> ChatService:
    """Return the process-wide chat service, creating it on first use."""
    global _service
    if _service is None:
        _service = ChatService(create_llm_client())
    return _service


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def post_chat(request: ChatRequest) -> ChatResponse:
    """Answer a chat message. Malformed or failed LLM output yields a safe fallback."""
    service = get_chat_service()
    try:
        reply = service.respond(
            user_message=request.message,
            cash=request.cash,
            positions=request.positions,
            watchlist=request.watchlist,
            prices=request.prices,
        )
    except Exception as exc:  # pragma: no cover - defensive boundary
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="chat assistant unavailable",
        ) from exc
    return ChatResponse(
        message=reply.message,
        trades=[TradeOut(ticker=t.ticker, side=t.side, quantity=t.quantity) for t in reply.trades],
        watchlist_changes=[
            WatchlistChangeOut(ticker=w.ticker, action=w.action) for w in reply.watchlist_changes
        ],
    )