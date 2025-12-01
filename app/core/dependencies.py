"""
Dependency injection helper functions for FastAPI.

This module provides dependency functions to access the dependency injection
container and services using FastAPI's Depends() pattern.
"""

import logging
from typing import TYPE_CHECKING, Annotated, cast

from fastapi import Depends, Request

if TYPE_CHECKING:
    from app.application.services.language_service import LanguageService
    from app.application.services.text_service import TextService
    from app.application.services.user_service import UserService
    from app.core.container import Container


logger = logging.getLogger(__name__)


def get_container(request: Request) -> "Container":
    """
    Get the DI container from FastAPI application state.

    This function retrieves the dependency injection container that was
    initialized during application startup and stored in app.state.

    Args:
        request: FastAPI Request object (injected automatically)

    Returns:
        Container instance with configured dependencies

    Example:
        >>> from fastapi import Depends
        >>> from app.core.dependencies import get_container
        >>> def endpoint(container: Container = Depends(get_container)):
        >>>     service = container.get_service(UserService)
    """
    container = cast("Container", request.app.state.container)
    logger.debug("Retrieved container from FastAPI application state")
    return container


def get_user_service(
    container: Annotated["Container", Depends(get_container)],
) -> "UserService":
    """
    Get the UserService instance via dependency injection.

    Args:
        container: DI container (injected automatically)

    Returns:
        UserService instance

    Example:
        >>> from fastapi import Depends
        >>> from app.core.dependencies import get_user_service
        >>> def endpoint(service: UserService = Depends(get_user_service)):
        >>>     users = service.get_all_users()
    """
    from app.application.services.user_service import UserService

    return container.get_service(UserService)


def get_text_service(
    container: Annotated["Container", Depends(get_container)],
) -> "TextService":
    """
    Get the TextService instance via dependency injection.

    Args:
        container: DI container (injected automatically)

    Returns:
        TextService instance
    """
    from app.application.services.text_service import TextService

    return container.get_service(TextService)


def get_language_service(
    container: Annotated["Container", Depends(get_container)],
) -> "LanguageService":
    """
    Get the LanguageService instance via dependency injection.

    Args:
        container: DI container (injected automatically)

    Returns:
        LanguageService instance

    Example:
        >>> from fastapi import Depends
        >>> from app.core.dependencies import get_language_service
        >>> def endpoint(service: LanguageService = Depends(get_language_service)):
        >>>     languages = service.get_all_languages()
    """
    from app.application.services.language_service import LanguageService

    return container.get_service(LanguageService)
