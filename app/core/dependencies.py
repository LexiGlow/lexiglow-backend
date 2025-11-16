"""
Dependency injection helper functions.

This module provides helper functions to access the dependency injection
container from Flask application context, making it easy to retrieve
services and repositories in endpoint handlers.
"""

import logging
from typing import TYPE_CHECKING, cast

from flask import current_app

if TYPE_CHECKING:
    from app.core.container import Container


logger = logging.getLogger(__name__)


def get_container() -> "Container":
    """
    Get the DI container from Flask application context.

    This function retrieves the dependency injection container that was
    initialized during application startup and stored in Flask's config.

    Returns:
        Container instance with configured dependencies

    Raises:
        RuntimeError: If called outside Flask application context
        KeyError: If container is not initialized in app config

    Example:
        >>> from app.core.dependencies import get_container
        >>> container = get_container()
        >>> user_service = container.get_user_service()
    """
    try:
        container = current_app.config["CONTAINER"]
        logger.debug("Retrieved container from Flask application context")
        return cast("Container", container)
    except RuntimeError as e:
        logger.error("Attempted to access container outside Flask context")
        raise RuntimeError(
            "Cannot access container outside Flask application context. "
            "This function must be called within a request context."
        ) from e
    except KeyError as e:
        logger.error("Container not found in Flask app config")
        raise KeyError(
            "DI Container not initialized in Flask application. "
            "Ensure create_app() properly initializes the container."
        ) from e
