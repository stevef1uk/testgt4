"""Acceptance tests for the API package boundary."""

from __future__ import annotations

import importlib


def test_api_package_imports_without_application_or_route_side_effects() -> None:
    package = importlib.import_module("app.api")

    assert package.__doc__ == "API package for the market application."
    assert not hasattr(package, "app")
    assert not hasattr(package, "router")