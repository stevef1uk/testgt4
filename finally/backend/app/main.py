from __future__ import annotations

import asyncio
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any

# Ensure backend root is on sys.path
_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))
_APP_DIR = Path(__file__).resolve().parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.ai.llm import build_messages, generate_chat_response
from app.market.cache import PriceCache
from app.market.gbm import GBMDataSimulator
from app.market.sse import format_sse_event
from app.portfolio.engine import (
    InsufficientCashError,
    InsufficientSharesError,
    PortfolioEngine,
    PortfolioError,
)
from db.schema import DEFAULT_USER_ID, DEFAULT_WATCHLIST, get_db_connection

# Static export of the Next.js frontend (next.config.js output: "export").
RIG_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_OUT = RIG_ROOT / "frontend" / "out"
INDEX_HTML = FRONTEND_OUT / "index.html"
DB_PATH = RIG_ROOT / "db" / "finally.db"

BASE_PRICES: dict[str, float] = {
    "AAPL": 190.50,
    "GOOGL": 175.20,
    "MSFT": 420.10,
    "AMZN": 185.30,
    "TSLA": 210.40,
    "NVDA": 125.80,
    "META": 490.60,
    "JPM": 195.20,
    "V": 275.40,
    "NFLX": 640.80,
}


def create_app() -> FastAPI:
    app = FastAPI(title="FinAlly", version="1.0.0")

    cache = PriceCache()
    for sym, p in BASE_PRICES.items():
        cache.update(sym, p)

    simulator = GBMDataSimulator(seed=42)

    def get_conn():
        return get_db_connection(DB_PATH)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/watchlist")
    def get_watchlist() -> dict[str, Any]:
        conn = get_conn()
        try:
            rows = conn.execute(
                "SELECT ticker FROM watchlist WHERE user_id = ? ORDER BY ticker",
                (DEFAULT_USER_ID,),
            ).fetchall()
            tickers_list = []
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            for r in rows:
                sym = r["ticker"]
                current_p = cache.get(sym) or BASE_PRICES.get(sym, 150.0)
                base_p = BASE_PRICES.get(sym, current_p)
                change = current_p - base_p
                change_pct = (change / base_p * 100.0) if base_p > 0 else 0.0
                direction = "up" if change > 0.001 else ("down" if change < -0.001 else "flat")
                tickers_list.append({
                    "ticker": sym,
                    "price": round(current_p, 2),
                    "previous_price": round(base_p, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_pct, 2),
                    "direction": direction,
                    "updated_at": now_iso,
                })
            return {"tickers": tickers_list}
        finally:
            conn.close()

    @app.post("/api/watchlist")
    async def add_watchlist(req: Request) -> dict[str, Any]:
        data = await req.json()
        ticker = (data.get("ticker") or "").strip().toUpperCase() if hasattr(str, "toUpperCase") else (data.get("ticker") or "").strip().upper()
        if not ticker:
            raise HTTPException(status_code=400, detail="ticker is required")
        conn = get_conn()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO watchlist (user_id, ticker) VALUES (?, ?)",
                (DEFAULT_USER_ID, ticker),
            )
            conn.commit()
            if not cache.get(ticker):
                cache.update(ticker, 100.0)
        finally:
            conn.close()
        return get_watchlist()

    @app.delete("/api/watchlist/{ticker}")
    def delete_watchlist(ticker: str) -> dict[str, Any]:
        sym = ticker.strip().upper()
        conn = get_conn()
        try:
            conn.execute(
                "DELETE FROM watchlist WHERE user_id = ? AND ticker = ?",
                (DEFAULT_USER_ID, sym),
            )
            conn.commit()
        finally:
            conn.close()
        return get_watchlist()

    @app.post("/api/reset")
    def reset_database() -> dict[str, str]:
        conn = get_conn()
        try:
            conn.execute("DELETE FROM trades")
            conn.execute("DELETE FROM positions")
            conn.execute("DELETE FROM portfolio_snapshots")
            conn.execute("DELETE FROM chat_messages")
            conn.execute("DELETE FROM watchlist WHERE user_id = ?", (DEFAULT_USER_ID,))
            conn.execute("UPDATE users_profile SET cash_balance = 10000.0 WHERE id = ?", (DEFAULT_USER_ID,))
            conn.executemany(
                "INSERT OR IGNORE INTO watchlist (user_id, ticker) VALUES (?, ?)",
                [(DEFAULT_USER_ID, ticker) for ticker in DEFAULT_WATCHLIST],
            )
            conn.commit()
            return {"status": "reset"}
        finally:
            conn.close()

    @app.get("/api/portfolio")
    def get_portfolio() -> dict[str, Any]:
        conn = get_conn()
        try:
            engine = PortfolioEngine(conn, DEFAULT_USER_ID)
            cash = engine.cash_balance()
            positions = engine.positions()
            positions_data = []
            total_equity = 0.0
            total_unrealized = 0.0
            for pos in positions:
                cur_price = cache.get(pos.ticker) or BASE_PRICES.get(pos.ticker, pos.avg_cost)
                market_val = pos.quantity * cur_price
                cost_val = pos.quantity * pos.avg_cost
                unrealized = market_val - cost_val
                total_equity += market_val
                total_unrealized += unrealized
                positions_data.append({
                    "ticker": pos.ticker,
                    "quantity": pos.quantity,
                    "avg_cost": round(pos.avg_cost, 2),
                    "current_price": round(cur_price, 2),
                    "unrealized_pnl": round(unrealized, 2),
                })
            return {
                "cash_balance": round(cash, 2),
                "total_value": round(cash + total_equity, 2),
                "unrealized_pnl": round(total_unrealized, 2),
                "positions": positions_data,
            }
        finally:
            conn.close()

    @app.post("/api/portfolio/trade")
    async def post_trade(req: Request) -> dict[str, Any]:
        data = await req.json()
        ticker = (data.get("ticker") or "").strip().upper()
        side = (data.get("side") or "").strip().lower()
        try:
            qty = float(data.get("quantity") or 0)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid quantity")

        if not ticker or qty <= 0 or side not in ("buy", "sell"):
            raise HTTPException(status_code=400, detail="Invalid trade parameters")

        conn = get_conn()
        try:
            engine = PortfolioEngine(conn, DEFAULT_USER_ID)
            price = cache.get(ticker) or BASE_PRICES.get(ticker, 150.0)
            if side == "buy":
                engine.buy(ticker, qty, price)
            else:
                engine.sell(ticker, qty, price)
            return {
                "status": "filled",
                "ticker": ticker,
                "quantity": qty,
                "side": side,
                "price": round(price, 2),
            }
        except InsufficientCashError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except InsufficientSharesError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except PortfolioError as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            conn.close()

    @app.post("/api/chat")
    async def post_chat(req: Request) -> dict[str, Any]:
        data = await req.json()
        message = (data.get("message") or "").strip()
        if not message:
            return {"reply": "Please enter a message.", "trade": None}

        conn = get_conn()
        try:
            portfolio_summary = get_portfolio()
            watchlist_resp = get_watchlist()
            engine = PortfolioEngine(conn, DEFAULT_USER_ID)

            messages = build_messages(message, portfolio_summary, watchlist_resp.get("tickers", []))
            key = os.environ.get("OPENROUTER_API_KEY", "")
            mock_mode = (
                os.environ.get("LLM_MOCK", "true").lower() in ("true", "1", "yes")
                or not key
                or key == "your-openrouter-api-key-here"
            )
            if mock_mode:
                await asyncio.sleep(0.3)
            result = generate_chat_response(messages, mock=mock_mode)

            trade = result.get("trade")
            if trade and isinstance(trade, dict):
                t_ticker = trade.get("ticker", "").upper()
                t_side = trade.get("side", "").lower()
                t_qty = float(trade.get("quantity", 0))
                if t_ticker and t_qty > 0 and t_side in ("buy", "sell"):
                    try:
                        p = cache.get(t_ticker) or BASE_PRICES.get(t_ticker, 150.0)
                        if t_side == "buy":
                            engine.buy(t_ticker, t_qty, p)
                        else:
                            engine.sell(t_ticker, t_qty, p)
                    except Exception as err:
                        result["reply"] = f"{result['reply']} (Trade failed: {err})"

            return result
        finally:
            conn.close()

    @app.get("/api/stream/prices")
    @app.get("/api/stream")
    async def stream_prices(request: Request):
        async def event_generator():
            while True:
                if await request.is_disconnected():
                    break
                conn = get_conn()
                try:
                    rows = conn.execute(
                        "SELECT ticker FROM watchlist WHERE user_id = ?",
                        (DEFAULT_USER_ID,),
                    ).fetchall()
                    tickers = [r["ticker"] for r in rows] or list(DEFAULT_WATCHLIST)
                finally:
                    conn.close()

                for sym in tickers:
                    old_p = cache.get(sym) or BASE_PRICES.get(sym, 100.0)
                    new_p = simulator.generate_next_price(old_p, volatility=0.20, drift=0.02)
                    cache.update(sym, new_p)
                    tick_data = {
                        "ticker": sym,
                        "price": round(new_p, 2),
                        "previous_price": round(old_p, 2),
                        "change": round(new_p - old_p, 2),
                        "change_percent": round((new_p - old_p) / old_p * 100.0, 2),
                        "direction": "up" if new_p >= old_p else "down",
                        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    }
                    yield format_sse_event("price", tick_data)
                    yield f"data: {json.dumps(tick_data)}\n\n"
                await asyncio.sleep(1.0)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # Mount static files last so API routes are never shadowed.
    if FRONTEND_OUT.is_dir():
        app.mount("/", StaticFiles(directory=str(FRONTEND_OUT), html=True), name="frontend")
    else:
        @app.get("/", include_in_schema=False)
        def frontend_unavailable() -> JSONResponse:
            return JSONResponse(
                status_code=503,
                content={"error": "Frontend export unavailable"},
            )

    return app


app = create_app()
