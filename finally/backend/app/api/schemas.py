"""Pydantic contracts for the FinAlly API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WatchlistRequest(APIModel):
    ticker: str = Field(min_length=1)

    @field_validator("ticker")
    @classmethod
    def ticker_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("ticker must not be blank")
        return value


class WatchlistItem(APIModel):
    ticker: str = Field(min_length=1)
    price: float = Field(ge=0)
    previous_price: float | None = Field(default=None, ge=0)
    timestamp: datetime | str
    change_direction: Literal["up", "down", "unchanged"] = "unchanged"


class TradeRequest(APIModel):
    ticker: str = Field(min_length=1)
    quantity: float = Field(gt=0)
    side: Literal["buy", "sell"]


class TradeResponse(APIModel):
    ticker: str
    quantity: float = Field(gt=0)
    side: Literal["buy", "sell"]
    price: float = Field(ge=0)
    cash: float
    message: str | None = None


class PortfolioPosition(APIModel):
    ticker: str = Field(min_length=1)
    quantity: float
    average_price: float = Field(ge=0)
    current_price: float = Field(ge=0)
    market_value: float = Field(ge=0)
    unrealized_pnl: float


class PortfolioResponse(APIModel):
    positions: list[PortfolioPosition] = Field(default_factory=list)
    cash: float
    total_value: float
    unrealized_pnl: float


class HistoryPoint(APIModel):
    timestamp: datetime | str
    value: float


class PortfolioHistory(APIModel):
    snapshots: list[HistoryPoint] = Field(default_factory=list)


class ChatRequest(APIModel):
    message: str = Field(min_length=1)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be blank")
        return value


class ChatAction(APIModel):
    action: str
    details: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(APIModel):
    message: str
    actions: list[ChatAction] = Field(default_factory=list)