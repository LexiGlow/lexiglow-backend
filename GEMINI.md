# LexiGlow Backend - LLM Guidelines

## Project Overview
The LexiGlow Backend is a REST API designed with a strong emphasis on clean architecture principles.  
It currently uses Flask but is transitioning to FastAPI, leveraging OpenAPI for API definition and documentation.  
The primary database is SQLite, with MongoDB with the ablolutelly same structure.

## Architecture & Structure
The project follows a Clean Architecture pattern to ensure separation of concerns, maintainability, and testability.

*   **`app/core/`**: Houses application-wide configurations, dependency management, logging, and security settings.
*   **`app/domain/`**: Encapsulates core business logic, defining entities, value objects, and interfaces for repositories. This layer is independent of external concerns.
*   **`app/infrastructure/`**: Provides concrete implementations for external services, such as database interactions (MongoDB with PyMongo, SQLite with SQLAlchemy) and other third-party integrations.
*   **`app/application/`**: Contains application services that orchestrate domain logic, handling specific use cases and coordinating interactions between the domain and infrastructure layers.
*   **`app/presentation/`**: Defines the API endpoints, handles HTTP requests, and manages request/response serialization (e.g., using Pydantic models for FastAPI).
*   **`tests/`**: Comprehensive suite for unit and integration tests.
*   **`data/`**: Stores local data, such as database files (ignored by git).
*   **`logs/`**: Stores application logs (ignored by git).
*   **`scripts/`**: Utility scripts for development tasks (e.g., database setup, data seeding, documentation generation).
*   **`docker/`**: Contains Docker-related configurations for containerized deployment.
*   **`app/presentation/api/v1/spec/openapi.yaml`**: The central OpenAPI specification document detailing all API endpoints and data models.

## Technology Stack
*   **Language**: Python 3.13.7
*   **Package Manager**: `pip` with `pyenv` for Python version control and `venv` for dependency management. (`uv` is also an option.)
*   **Database**: SQLite (primary, via SQLAlchemy), MongoDB (the same structure with SQL, via PyMongo).
*   **API Documentation**: OpenAPI 3.0 (Swagger UI).
*   **Testing Framework**: `pytest`.
*   **Code Quality**: `mypy` (static type checker), `ruff` (linter and formatter).
*   **CORS**: Enabled for cross-origin requests.

## Coding Standards & Best Practices

### Python Style
*   Adhere strictly to `ruff` for linting and formatting, with a strict line length limit of 88 characters.
*   Follow PEP 8 conventions.
*   Avoid imports in the middle of files; place them at the top.
*   Follow `mypy` rules strictly when writing code.
*   Use only the custom logger configured in `app/core/logging_config.py` for all logging.
*   Utilize type hints extensively for improved code clarity and maintainability.
*   Prefer f-strings for string formatting.
*   Use `pathlib.Path` for all file system operations.
*   Write comprehensive docstrings for all modules, classes, and functions.
*   Employ meaningful and descriptive variable, function, and class names.
*   Keep functions and methods small, focused, and single-purpose.

### API Design (FastAPI-focused)
*   Design APIs following RESTful principles.
*   Use appropriate HTTP status codes for responses (e.g., 200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Internal Server Error).
*   Define all API endpoints and data models in `openapi/openapi.yaml`.
*   Leverage FastAPI's automatic request and response validation using Pydantic models.
*   Implement dependency injection for managing services in the `app/application/services/` and data repositories.
*   Ensure API endpoints return serialized data using Pydantic schemas.

### Database Interaction
*   Abstract database operations behind well-defined repository interfaces in the `app/domain/interfaces/` layer.
*   Provide concrete repository implementations in `app/infrastructure/database/`.
*   Use the appropriate Object-Document Mapper (ODM) or Object-Relational Mapper (ORM) for each database (PyMongo for MongoDB, SQLAlchemy for SQLite).
*   Implement robust error handling for all database operations.

### Error Handling
*   Maintain a consistent error response format across the API.
*   Utilize the configured logging system (`app/core/logging_config.py`) for all error reporting.
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Operation completed successfully")
logger.error(f"Error occurred: {error}")
```
*   Gracefully handle exceptions from external services and database interactions.

### Configuration
*   Manage application configuration using environment variables, typically loaded from a `.env` file via `python-dotenv`.
*   Store all sensitive information (e.g., API keys, database credentials) in environment variables and never commit them to version control.
*   Provide sensible default values for configuration parameters.
*   Centralize application configuration in `app/core/config.py`.

## Development Workflow
1.  **API Definition**: Start by defining or updating API endpoints and data models in `openapi/openapi.yaml`.
2.  **Core Logic**: Implement domain logic, application services, and infrastructure components.
3.  **API Implementation**: Develop API endpoints in `app/presentation/` that utilize the application and domain layers.
4.  **Testing**: Write comprehensive unit and integration tests for new and modified code.
5.  **Code Quality Checks**: During the code generation run `mypy` for type checking and`ruff` for linting and formatting.
6.  **Local Testing**: Test API functionality using Swagger UI (available at `/docs` endpoint) or `curl`.
7.  **Documentation**: Generate project documentation using `scripts/generate_docs.py` as needed.

## Testing
*   All tests are executed using `pytest`.
*   Tests are organized into `tests/unit` and `tests/integration` directories.
*   External dependencies (e.g., databases, third-party APIs) should be mocked during unit tests.
*   Ensure both successful execution paths and error handling scenarios are covered by tests.

## Security Considerations
*   Validate all incoming request data rigorously using Pydantic models to prevent injection attacks and other vulnerabilities.
*   Utilize environment variables for all sensitive configuration parameters.
*   Properly configure CORS policies to restrict access to authorized origins.
*   Implement robust authentication and authorization mechanisms as required.
*   Sanitize all database queries and inputs to prevent SQL injection (for SQLite) and similar attacks.