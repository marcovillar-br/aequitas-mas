"""FastAPI application entrypoint for the Aequitas-MAS gateway."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.api.dependencies import get_checkpointer
from src.api.routers.analyze import router as analyze_router
from src.api.routers.backtest import router as backtest_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize shared API dependencies and close them when supported."""
    checkpointer = get_checkpointer()
    try:
        yield
    finally:
        aclose = getattr(checkpointer, "aclose", None)
        if callable(aclose):
            await aclose()
            return

        close = getattr(checkpointer, "close", None)
        if callable(close):
            close()


def create_app() -> FastAPI:
    """Create the FastAPI application with all registered routers."""
    application = FastAPI(
        title="Aequitas-MAS API",
        version="6.0.0",
        lifespan=lifespan,
    )
    application.include_router(analyze_router)
    application.include_router(backtest_router)
    return application


app = create_app()
