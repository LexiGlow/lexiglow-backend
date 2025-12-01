import logging
import logging.config

from fastapi import FastAPI

from app.core.app_initializer import AppInitializer
from app.core.logging_config import LOGGING_CONFIG

# --- Auto-configure logging on module import ---
# This ensures logging is configured before any other modules create loggers
logging.config.dictConfig(LOGGING_CONFIG)


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    This is a convenience function that delegates to AppInitializer.create_app().

    Returns:
        FastAPI application instance with configured middleware and routes
    """
    return AppInitializer.create_app()
