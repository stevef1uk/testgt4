"""FastAPI application entry point for the StockPilot backend.

Later phases register the portfolio, watchlist, and chat routers here.
"""

from fastapi import FastAPI

app = FastAPI(title="StockPilot", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}