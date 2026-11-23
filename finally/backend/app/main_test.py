"""Foundation integration tests for app.main.create_app (plan.md: Project Foundation)."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import create_app, INDEX_HTML


TICKERS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "NFLX"]


def test_create_app_returns_fastapi():
    app = create_app()
    assert isinstance(app, FastAPI)


def test_health_route_registered():
    app = create_app()
    paths = {r.path for r in app.routes}
    assert "/api/health" in paths


def test_root_route_registered():
    app = create_app()
    paths = {r.path for r in app.routes}
    assert "/" in paths


def test_health_endpoint_returns_ok():
    client = TestClient(create_app())
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_root_returns_real_export_with_dashboard_heading():
    client = TestClient(create_app())
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.text
    assert "FinAlly Trading Workstation" in body


def test_root_contains_all_ten_tickers():
    client = TestClient(create_app())
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.text
    for ticker in TICKERS:
        assert ticker in body, f"missing ticker {ticker} in root export"


def test_root_contains_portfolio_value():
    client = TestClient(create_app())
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.text
    assert "$10,000" in body


def test_root_excludes_fallback_or_placeholder_html():
    client = TestClient(create_app())
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    body = resp.text
    # genuine exported Next.js HTML: has doctype, head, body, FinAlly heading
    assert "<!DOCTYPE html>" in body
    assert "<html lang=" in body
    assert "FinAlly Trading Workstation" in body
    # never a synthesized placeholder served from Python
    assert "placeholder" not in body.lower()
    assert "synthesized" not in body.lower()


def test_root_returns_503_when_export_absent(monkeypatch):
    import app.main as main

    monkeypatch.setattr(main, "INDEX_HTML", main.RIG_ROOT / "frontend" / "out" / "does-not-exist.html")
    client = TestClient(create_app())
    resp = client.get("/")
    assert resp.status_code == 503
    payload = resp.json()
    assert "error" in payload
    assert "detail" in payload
    assert "frontend export not found" in payload["error"]
    # must never fall back to placeholder/dashboard HTML
    assert "<html" not in resp.text
    assert "FinAlly" not in resp.text