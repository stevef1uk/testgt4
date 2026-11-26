"""Package marker and FastAPI route-factory export for the SPEC Section 8 API layer.

Route contracts live in ``schemas.py``. ``main.py`` builds the application through
``create_app`` and passes in the routers it wants mounted.
"""

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import FastAPI


def create_app(routers: Iterable[Any] = ()) -> "FastAPI":
    """Build the FastAPI application and include each router in ``routers``.

    FastAPI is imported inside the function so importing ``app.api`` (for example
    to reach ``schemas``) does not require the web framework to be installed.
    """
    from fastapi import FastAPI

    app = FastAPI(title="FinAlly")
    for router in routers:
        app.include_router(router)
    return app


__all__ = ["create_app"]