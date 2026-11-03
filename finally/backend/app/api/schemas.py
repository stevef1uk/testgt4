"""Pydantic contracts for the canonical API endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, validator


class WatchlistRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=10)

    @validator("ticker")
    def normalize_ticker(cls, value: str) -> str:
        ticker = value.strip().upper()
        if not ticker.isalpha():
            raise ValueError("ticker must contain only letters")
        return ticker


class TradeRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=10)
    quantity: float = Field(gt=0)
    side: Literal["buy", "sell"]

    @validator("ticker")
    def normalize_ticker(cls, value: str) -> str:
        ticker = value.strip().upper()
        if not ticker.isalpha():
            raise ValueError("ticker must contain only letters")
        return ticker


class TradeAction(TradeRequest):
    pass


class WatchlistChange(BaseModel):
    ticker: str = Field(min_length=1, max_length=10)
    action: Literal["add", "remove"]

    @validator("ticker")
    def normalize_ticker(cls, value: str) -> str:
        ticker = value.strip().upper()
        if not ticker.isalpha():
            raise ValueError("ticker must contain only letters")
        return ticker


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    message: str
    trades: list[TradeAction] = Field(default_factory=list)
    watchlist_changes: list[WatchlistChange] = Field(default_factory=list)


class PriceQuote(BaseModel):
    ticker: str
    price: float
    change_percent: float = 0.0


class Position(BaseModel):
    ticker: str
    shares: float
    average_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float


class PortfolioResponse(BaseModel):
    cash: float
    positions: list[Position] = Field(default_factory=list)
    total_value: float
    unrealized_pnl: float


class PortfolioSnapshot(BaseModel):
    timestamp: str
    total_value: float
    cash: float


class PriceEvent(BaseModel):
    prices: list[PriceQuote] = Field(default_factory=list)


__all__ = [
    "ChatRequest",
    "ChatResponse",
    "PortfolioResponse",
    "PortfolioSnapshot",
    "Position",
    "PriceEvent",
    "PriceQuote",
    "TradeAction",
    "TradeRequest",
    "WatchlistChange",
    "WatchlistRequest",
]