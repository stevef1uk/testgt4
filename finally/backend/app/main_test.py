"""Tests for the FinAlly FastAPI entry point (backend/app/main.py).

Covers:
- GET /api/health returns HTTP 200 with {"status": "ok"}.
- GET / serves the real dashboard (heading, brand, ten default tickers, $10,000 cash)
  when the Next.js static export exists.
- Static mount does not shadow API routes.
- Missing frontend export returns 503 with a JSON error body (no placeholder page).
- create_app() yields independent application instances.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest
from fastapi.testclient import TestClient

_MAIN_PATH = Path(__file__).resolve().parent / "main.py"

DEFAULT_TICKERS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "NFLX"]


def _load_main() -> ModuleType:
    """Load backend/app/main.py by file path (no sys.path manipulation)."""
    spec = importlib.util.spec_from_file_location("finally_backend_app_main", _MAIN_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def main_module() -> ModuleType:
    return _load_main()


def _dashboard_html() -> str:
    rows = "".join(f"<tr><td>{t}</td><td>$0.00</td></tr>" for t in DEFAULT_TICKERS)
    return (
        "<!DOCTYPE html><html><head><title>FinAlly</title></head><body>"
        "<span>FinAlly</span>"
        "<h1>Trading dashboard</h1>"
        "<div>Cash $10,000</div>"
        f"<table><tbody>{rows}</tbody></table>"
        "</body></html>"
    )


@pytest.fixture
def frontend_out(tmp_path: Path) -> Path:
    """A fake Next.js static export containing the dashboard index.html."""
    out = tmp_path / "out"
    out.mkdir()
    (out / "index.html").write_text(_dashboard_html(), encoding="utf-8")
    return out


def test_health_returns_ok_status(main_module: ModuleType, tmp_path: Path) -> None:
    # Missing export dir: health must still work regardless of frontend.
    main_module.FRONTEND_OUT = tmp_path / "does-not-exist"
    client = TestClient(main_module.create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_serves_real_dashboard_content(main_module: ModuleType, frontend_out: Path) -> None:
    main_module.FRONTEND_OUT = frontend_out
    client = TestClient(main_module.create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Real dashboard content, per SPEC "GET / must render the actual dashboard".
    assert "<h1>Trading dashboard</h1>" in response.text
    assert "FinAlly" in response.text
    for ticker in DEFAULT_TICKERS:
        assert f"<td>{ticker}</td>" in response.text
    assert "$10,000" in response.text


def test_health_not_shadowed_by_static_mount(main_module: ModuleType, frontend_out: Path) -> None:
    # Static mount is at "/"; API routes registered first must still win.
    main_module.FRONTEND_OUT = frontend_out
    client = TestClient(main_module.create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "Trading dashboard" not in response.text


def test_root_503_when_frontend_export_missing(main_module: ModuleType, tmp_path: Path) -> None:
    main_module.FRONTEND_OUT = tmp_path / "missing-out"
    client = TestClient(main_module.create_app())

    response = client.get("/")

    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["error"] == "Frontend export unavailable"
    # No placeholder page may be served in place of the dashboard.
    assert "<html" not in response.text.lower()


def test_root_503_body_does_not_contain_dashboard(main_module: ModuleType, tmp_path: Path) -> None:
    main_module.FRONTEND_OUT = tmp_path / "missing-out"
    client = TestClient(main_module.create_app())

    response = client.get("/")

    assert "Trading dashboard" not in response.text
    assert "$10,000" not in response.text


def test_unknown_api_path_is_404(main_module: ModuleType, frontend_out: Path) -> None:
    main_module.FRONTEND_OUT = frontend_out
    client = TestClient(main_module.create_app())

    response = client.get("/api/does-not-exist")

    assert response.status_code == 404


def test_create_app_returns_independent_instances(main_module: ModuleType, tmp_path: Path) -> None:
    main_module.FRONTEND_OUT = tmp_path / "missing-out"
    first = main_module.create_app()
    second = main_module.create_app()

    assert first is not second
    assert TestClient(first).get("/api/health").status_code == 200
    assert TestClient(second).get("/api/health").status_code == 200
