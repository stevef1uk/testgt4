"""Backend API tests for the REST surface under /api/* and GET /.

Covers plan.md te-2iz acceptance:
- GET / serves the dashboard export and returns 503 with a diagnostic body
  when the export is missing.
- Watchlist and trade endpoints operate on the single user "default" and
  market orders fill instantly at the cached price.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import app.db.connection as connection_module  # noqa: E402
import app.main as main_module  # noqa: E402
from app.db.seed import initialize_database  # noqa: E402
from app.portfolio import engine as portfolio_engine  # noqa: E402
from app.portfolio import repository as portfolio_repo  # noqa: E402
from app.portfolio import repository as repository_module  # noqa: E402

API_TEST_PRICES = {
    "AAPL": 150.0,
    "NVDA": 120.0,
    "MSFT": 300.0,
    "GOOGL": 140.0,
    "AMZN": 180.0,
    "TSLA": 200.0,
}


@pytest.fixture(autouse=True)
def price_source_fixture() -> Iterator[None]:
    portfolio_engine.set_price_source(lambda ticker: API_TEST_PRICES.get(ticker))
    yield
    portfolio_engine.set_price_source(lambda ticker: None)

DEFAULT_TICKERS = [
    "AAPL",
    "GOOGL",
    "MSFT",
    "AMZN",
    "TSLA",
    "NVDA",
    "META",
    "JPM",
    "V",
    "NFLX",
]

DASHBOARD_HTML = (
    "<html><body><h1>FinAlly</h1><p>Cash: $10,000.00</p>"
    + "".join(f"<span>{t}</span>" for t in DEFAULT_TICKERS)
    + "</body></html>"
)


@pytest.fixture
def db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Point the app at a fresh, seeded SQLite file for this test only.

    The portfolio repository caches a module-level connection, so it must be
    replaced explicitly; patching DEFAULT_DB_PATH alone does not reach it.
    """
    path = tmp_path / "finally.db"
    monkeypatch.setattr(connection_module, "DEFAULT_DB_PATH", path)
    initialize_database(str(path))
    conn = connection_module.connect(path)
    repository_module.set_connection(conn)
    yield path
    repository_module.set_connection(connection_module.connect(":memory:"))
    conn.close()


@pytest.fixture
def client(
    db_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    """TestClient with a dashboard export placed where GET / reads it."""
    index = tmp_path / "frontend_out" / "index.html"
    index.parent.mkdir()
    index.write_text(DASHBOARD_HTML, encoding="utf-8")
    monkeypatch.setattr(main_module, "FRONTEND_INDEX", index)
    with TestClient(main_module.create_app()) as c:
        yield c


# --- GET / (dashboard) -------------------------------------------------------


def test_root_serves_dashboard_html(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "FinAlly" in resp.text


def test_root_serves_export_content_unchanged(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.text == DASHBOARD_HTML


def test_root_returns_503_with_diagnostic_when_export_missing(
    db_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = tmp_path / "absent" / "index.html"
    monkeypatch.setattr(main_module, "FRONTEND_INDEX", missing)
    with TestClient(main_module.create_app()) as c:
        resp = c.get("/")
    assert resp.status_code == 503
    assert "Frontend export missing" in resp.text
    assert "npm run build" in resp.text


# --- Watchlist: single user "default" ---------------------------------------


def test_watchlist_defaults_to_ten_tickers(client: TestClient) -> None:
    resp = client.get("/api/watchlist")
    assert resp.status_code == 200
    symbols = sorted(item["ticker"] for item in resp.json())
    assert symbols == sorted(DEFAULT_TICKERS)


def test_watchlist_add_then_remove_ticker(client: TestClient) -> None:
    add = client.post("/api/watchlist", json={"ticker": "PYPL"})
    assert add.status_code == 201
    assert "PYPL" in [item["ticker"] for item in add.json()]

    rm = client.delete("/api/watchlist/PYPL")
    assert rm.status_code == 200
    assert "PYPL" not in [item["ticker"] for item in rm.json()]


def test_watchlist_rejects_duplicate_ticker(client: TestClient) -> None:
    resp = client.post("/api/watchlist", json={"ticker": "AAPL"})
    assert resp.status_code == 409


def test_watchlist_remove_missing_ticker_returns_404(client: TestClient) -> None:
    resp = client.delete("/api/watchlist/ZZZZ")
    assert resp.status_code == 404


# --- Portfolio: single user "default", market orders fill instantly ---------


def test_initial_portfolio_has_ten_thousand_cash(client: TestClient) -> None:
    resp = client.get("/api/portfolio")
    assert resp.status_code == 200
    assert resp.json()["cash_balance"] == pytest.approx(10_000.0)


def test_buy_market_order_fills_and_debits_cash(client: TestClient) -> None:
    resp = client.post(
        "/api/portfolio/trade",
        json={"ticker": "AAPL", "quantity": 2, "side": "buy"},
    )
    assert resp.status_code == 201

    data = client.get("/api/portfolio").json()
    aapl = next(p for p in data["positions"] if p["ticker"] == "AAPL")
    assert aapl["quantity"] == 2
    assert data["cash_balance"] < 10_000


def test_sell_without_position_is_rejected(client: TestClient) -> None:
    resp = client.post(
        "/api/portfolio/trade",
        json={"ticker": "AAPL", "quantity": 1, "side": "sell"},
    )
    assert resp.status_code == 400


def test_buy_exceeding_cash_is_rejected(client: TestClient) -> None:
    resp = client.post(
        "/api/portfolio/trade",
        json={"ticker": "NVDA", "quantity": 1_000_000, "side": "buy"},
    )
    assert resp.status_code == 400
    assert client.get("/api/portfolio").json()["cash_balance"] == pytest.approx(10_000.0)