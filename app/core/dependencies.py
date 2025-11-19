"""
Dependency injection helper functions for FastAPI.

This module provides dependency functions to access the dependency injection
container and services using FastAPI's Depends() pattern.
"""

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request

if TYPE_CHECKING:
    from app.application.services.user_service import UserService
    from app.core.container import Container
    from app.domain.interfaces.language_repository import ILanguageRepository
    from app.domain.interfaces.text_repository import ITextRepository
    from app.domain.interfaces.user_repository import IUserRepository


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
        >>>     service = container.get_user_service()
    """
    container = request.app.state.container
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
    return container.get_user_service()


def get_user_repository(
    container: Annotated["Container", Depends(get_container)],
) -> "IUserRepository":
    """
    Get the UserRepository instance via dependency injection.

    Args:
        container: DI container (injected automatically)

    Returns:
        IUserRepository implementation instance
    """
    return container.get_user_repository()


def get_language_repository(
    container: Annotated["Container", Depends(get_container)],
) -> "ILanguageRepository":
    """
    Get the LanguageRepository instance via dependency injection.

    Args:
        container: DI container (injected automatically)

    Returns:
        ILanguageRepository implementation instance
    """
    return container.get_language_repository()


def get_text_repository(
    container: Annotated["Container", Depends(get_container)],
) -> "ITextRepository":
    """
    Get the TextRepository instance via dependency injection.

    Args:
        container: DI container (injected automatically)

    Returns:
        ITextRepository implementation instance
    """
    return container.get_text_repository()
