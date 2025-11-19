import logging
import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.container import Container
from app.core.logging_config import LOGGING_CONFIG

# --- Auto-configure logging on module import ---
# This ensures logging is configured before any other modules create loggers
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    Returns:
        FastAPI application instance with configured middleware and routes
    """
    # Create the FastAPI application instance
    app = FastAPI(
        title="LexiGlow API",
        description="The official API for LexiGlow, a language learning application.",
        version="0.1.0",
        contact={
            "name": "API Support",
            "email": "support@lexiglow.com",
        },
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS middleware
    # TODO: Review and restrict origins for production deployment
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )
    logger.info("CORS middleware configured")

    # Initialize dependency injection container
    container = Container()
    app.state.container = container
    logger.info("Dependency injection container initialized and configured")

    # Import and include routers
    from app.presentation.api.v1 import about, health, users

    app.include_router(health.router, tags=["Health"])
    app.include_router(about.router, tags=["About"])
    app.include_router(users.router, tags=["Users"])
    logger.info("API routers registered")

    return app
