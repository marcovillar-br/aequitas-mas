"""AWS Lambda serverless entrypoint for the FastAPI application."""

from __future__ import annotations

from mangum import Mangum

from src.api.app import app

handler = Mangum(app, lifespan="on")
