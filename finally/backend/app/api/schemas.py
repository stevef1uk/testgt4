"""Pydantic route contracts for SPEC Section 8. No database access."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TickData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str
    price: float
    previous_price: float
    timestamp: str
    direction: Literal["up", "down", "flat"]


class PortfolioSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cash_balance: float
    total_value: float
    unrealized_pnl: float


class PortfolioSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: str
    total_value: float


class TradeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str
    quantity: float = Field(gt=0)
    side: Literal["buy", "sell"]


class TradeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str
    quantity: float
    side: Literal["buy", "sell"]
    price: float
    cash_balance: float


class WatchlistResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tickers: list[str]


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str


class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: ChatMessage
    trades: list[TradeRequest] = Field(default_factory=list)