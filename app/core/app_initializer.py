"""
Application initializer for LexiGlow Backend.

This module provides the AppInitializer class which encapsulates all
application initialization logic including repository factory creation,
service mapping configuration, and router registration.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.container import Container

logger = logging.getLogger(__name__)


class AppInitializer:
    """
    Static class for initializing the FastAPI application.

    This class encapsulates all application initialization logic including
    repository factory creation, service mapping configuration, and router registration.
    """

    @staticmethod
    def create_app() -> FastAPI:
        """
        Creates and configures the FastAPI application.

        Returns:
            FastAPI application instance with configured middleware and routes
        """
        # Create the FastAPI application instance
        app = FastAPI(
            title="LexiGlow API",
            description=(
                "The official API for LexiGlow, a language learning application."
            ),
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

        # Initialize repository factory
        repository_factory = AppInitializer.__create_repository_factory()

        # Create service mapping
        service_mapping = AppInitializer.__create_service_mapping()

        # Initialize dependency injection container
        container = Container(
            repository_factory=repository_factory, service_mapping=service_mapping
        )
        app.state.container = container
        logger.info("Dependency injection container initialized and configured")

        # Register routers
        AppInitializer.__register_routers(app)
        logger.info("API routers registered")

        # Add shutdown event handler for async engine cleanup
        @app.on_event("shutdown")
        async def shutdown_event():
            """Clean up database connections on shutdown."""
            from app.core.config import ACTIVE_DATABASE_TYPE

            if ACTIVE_DATABASE_TYPE == "sqlite":
                from app.infrastructure.database.sqlite import SQLiteRepositoryFactory

                if SQLiteRepositoryFactory._shared_async_engine is not None:
                    await SQLiteRepositoryFactory._shared_async_engine.dispose()
                    logger.info("SQLite async engine disposed")

        return app

    @staticmethod
    def __create_repository_factory():
        """
        Create repository factory based on configuration.

        Returns:
            Repository factory instance
            (SQLiteRepositoryFactory or MongoDBRepositoryFactory)

        Raises:
            ValueError: If database type is unsupported or MONGO_URI is missing
        """
        from app.core.config import ACTIVE_DATABASE_TYPE, MONGO_URI
        from app.domain.interfaces.repository_factory import IRepositoryFactory

        repository_factory: IRepositoryFactory

        if ACTIVE_DATABASE_TYPE == "sqlite":
            from app.infrastructure.database.sqlite import SQLiteRepositoryFactory

            repository_factory = SQLiteRepositoryFactory()
            logger.info("SQLite repository factory initialized")
        elif ACTIVE_DATABASE_TYPE == "mongodb":
            from app.infrastructure.database.mongodb import MongoDBRepositoryFactory

            if MONGO_URI is None:
                raise ValueError("MONGO_URI must be set for MongoDB database")
            repository_factory = MongoDBRepositoryFactory(
                db_url=MONGO_URI,
                db_name="lexiglow",
            )
            logger.info("MongoDB repository factory initialized")
        else:
            raise ValueError(f"Unsupported database type: {ACTIVE_DATABASE_TYPE}")

        return repository_factory

    @staticmethod
    def __create_service_mapping() -> dict[type, type]:
        """
        Create service mapping configuration.

        Returns:
            Dictionary mapping service types to their required repository types
        """
        from app.application.services.user_service import UserService
        from app.domain.interfaces.user_repository import IUserRepository

        service_mapping: dict[type, type] = {
            UserService: IUserRepository,
        }
        return service_mapping

    @staticmethod
    def __register_routers(app: FastAPI) -> None:
        """
        Register API routers with the FastAPI application.

        Args:
            app: FastAPI application instance
        """
        from app.presentation.api.v1 import about, health, users

        app.include_router(health.router, tags=["Health"])
        app.include_router(about.router, tags=["About"])
        app.include_router(users.router, tags=["Users"])
