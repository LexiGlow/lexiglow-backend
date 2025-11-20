"""
Dependency Injection Container for LexiGlow Backend.

This module provides a lightweight dependency injection container that manages
the lifecycle of repositories and services, enabling centralized dependency
configuration and easy testing with mock dependencies.
"""

import logging
from typing import Any, cast

from app.domain.interfaces.repository_factory import IRepositoryFactory

logger = logging.getLogger(__name__)


class Container:
    """
    Dependency injection container for managing application dependencies.

    This container implements the singleton pattern for services and delegates
    repository creation to the repository factory. It supports dependency
    overrides for testing purposes.

    Attributes:
        _repository_factory: Factory for creating repository instances
        _services: Cache of instantiated service instances
        _overrides: Map of interface types to override implementations
        _service_mapping: Map of service types to their required repository types
    """

    def __init__(
        self,
        repository_factory: IRepositoryFactory,
        service_mapping: dict[type, type],
    ):
        """
        Initialize the DI container with a repository factory.

        Args:
            repository_factory: Factory instance for creating repositories
            service_mapping: Map of service types to their required repository types.
                           Must not be None.

        Raises:
            ValueError: If service_mapping is None or empty
        """
        if service_mapping is None:
            raise ValueError("service_mapping cannot be None")
        if not service_mapping:
            raise ValueError("service_mapping cannot be empty")

        self._repository_factory = repository_factory
        self._services: dict[type, Any] = {}
        self._overrides: dict[type, Any] = {}
        self._service_mapping: dict[type, type] = service_mapping

        logger.info("DI Container initialized")

    def register_override(self, interface: type, implementation: Any) -> None:
        """
        Register an override for dependency injection (primarily for testing).

        Args:
            interface: The interface or class type to override
            implementation: The override implementation (instance or class)
        """
        self._overrides[interface] = implementation
        logger.debug(f"Registered override for {interface.__name__}")

    def clear_overrides(self) -> None:
        """Clear all registered overrides."""
        self._overrides.clear()
        logger.debug("Cleared all dependency overrides")

    def reset(self) -> None:
        """
        Reset the container by clearing all caches and overrides.

        This is useful for testing to ensure a clean state between tests.
        """
        self._services.clear()
        self._overrides.clear()
        logger.debug("Container reset: cleared all caches and overrides")

    def get_repository[T](self, repository_type: type[T]) -> T:
        """
        Get a repository instance by type.

        Args:
            repository_type: The repository interface type
                           (e.g., IUserRepository, ILanguageRepository)

        Returns:
            Repository instance implementing the interface

        Raises:
            ValueError: If repository type is not supported
            Exception: If repository instantiation fails

        Example:
            >>> container = Container(repository_factory)
            >>> user_repo = container.get_repository(IUserRepository)
        """
        # Check for override first
        if repository_type in self._overrides:
            override = self._overrides[repository_type]
            if isinstance(override, type):
                return cast(T, override())
            return cast(T, override)

        # Use repository factory (factory handles caching)
        try:
            logger.debug(f"Getting {repository_type.__name__} from factory")
            instance = self._repository_factory.get_repository(repository_type)
            logger.info(f"{repository_type.__name__} retrieved")
            return instance
        except Exception as e:
            logger.error(
                f"Failed to get {repository_type.__name__}: {e}", exc_info=True
            )
            raise

    def get_service[T](self, service_type: type[T]) -> T:
        """
        Get a service instance by type (singleton).

        Args:
            service_type: The service class type (e.g., UserService)

        Returns:
            Service instance of the specified type

        Raises:
            ValueError: If service type is not registered
            Exception: If service instantiation fails

        Example:
            >>> container = Container(repository_factory)
            >>> user_service = container.get_service(UserService)
        """
        # Check for override first
        if service_type in self._overrides:
            override = self._overrides[service_type]
            if isinstance(override, type):
                return cast(T, override())
            return cast(T, override)

        # Check service cache first
        if service_type in self._services:
            logger.debug(f"Returning cached {service_type.__name__} instance")
            return cast(T, self._services[service_type])

        # Create new instance
        try:
            logger.debug(f"Creating {service_type.__name__} instance")
            instance = self._create_service(service_type)
            self._services[service_type] = instance
            logger.info(f"{service_type.__name__} initialized and cached")
            return instance
        except Exception as e:
            logger.error(
                f"Failed to create {service_type.__name__}: {e}", exc_info=True
            )
            raise

    def _create_service[T](self, service_type: type[T]) -> T:
        """
        Universal method to create a service instance with its dependencies.

        Args:
            service_type: The service class type (e.g., UserService)

        Returns:
            Service instance with injected dependencies

        Raises:
            ValueError: If service type is not registered or repository dependency
                       is not found
        """
        if service_type not in self._service_mapping:
            raise ValueError(
                f"Service type {service_type.__name__} is not registered. "
                f"Available types: {list(self._service_mapping.keys())}"
            )

        repository_type = self._service_mapping[service_type]
        logger.debug(
            f"Creating {service_type.__name__} with {repository_type.__name__}"
        )
        repo: Any = self.get_repository(repository_type)
        service_cls = cast(type[Any], service_type)
        return cast(T, service_cls(repo))

    def __repr__(self) -> str:
        """Return string representation of the container state."""
        service_names = [s.__name__ for s in self._services.keys()]
        return f"Container(services={service_names}, overrides={len(self._overrides)})"
