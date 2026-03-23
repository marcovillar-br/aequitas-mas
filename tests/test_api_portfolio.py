"""Integration tests for portfolio endpoint registration in the FastAPI app."""

from __future__ import annotations

from src.api.app import create_app
from src.core.state import PortfolioOptimizationResult


def test_create_app_registers_portfolio_post_route() -> None:
    """The FastAPI application must expose the POST /portfolio endpoint."""
    application = create_app()

    matching_routes = [
        route
        for route in application.routes
        if getattr(route, "path", None) == "/portfolio"
    ]

    assert len(matching_routes) == 1
    assert "POST" in matching_routes[0].methods


def test_portfolio_route_declares_structured_response_model() -> None:
    """The registered route must expose the deterministic optimizer response contract."""
    application = create_app()
    route = next(route for route in application.routes if getattr(route, "path", None) == "/portfolio")

    assert route.response_model is PortfolioOptimizationResult
