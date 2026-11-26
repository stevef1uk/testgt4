"""Tests for the API package router and factory."""

from fastapi.testclient import TestClient

from app.api import create_app, router


def test_router_exposes_only_health() -> None:
    routes = {(r.path, tuple(sorted(r.methods))) for r in router.routes}
    assert routes == {("/api/health", ("GET",))}


def test_create_app_serves_health() -> None:
    client = TestClient(create_app())
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}