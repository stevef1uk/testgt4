import importlib


def test_api_package_is_importable_without_side_effects() -> None:
    module = importlib.import_module("app.api")

    assert module.__name__ == "app.api"
    assert module.__package__ == "app.api"