"""Pydantic v2 request/response models for the portfolio API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TradeRequest(BaseModel):
    """Payload for POST /api/portfolio/trades."""

    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(min_length=1, max_length=16)
    side: Literal["buy", "sell"]
    quantity: float = Field(gt=0)


class PositionOut(BaseModel):
    """A single open position with its current valuation."""

    model_config = ConfigDict(from_attributes=True)

    ticker: str
    quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float


class PortfolioOut(BaseModel):
    """Current portfolio state returned by GET /api/portfolio."""

    cash_balance: float
    total_value: float
    positions: list[PositionOut] = Field(default_factory=list)


class TradeOut(BaseModel):
    """Result of an executed trade."""

    id: int
    ticker: str
    side: Literal["buy", "sell"]
    quantity: float
    price: float
    executed_at: datetime


class SnapshotOut(BaseModel):
    """One point in the portfolio value history."""

    total_value: float
    recorded_at: datetime