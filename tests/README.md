# Tests

This directory contains the tests for the LexiGlow backend application. The tests are divided into two main categories: unit tests and integration tests.

## Test Structure

The test suite is organized into the following directories:

-   `unit/`: Contains unit tests for individual components of the application. These tests are isolated and do not require any external dependencies.
-   `integration/`: Contains integration tests that verify the interaction between different components of the application. These tests may require a running database or other external services.

### Unit Tests

The unit tests are further organized by the application layer they are testing:

-   `application/services/`: Tests for the application services.
-   `infrastructure/database/`: Tests for the database repositories (both MongoDB and SQLite implementations).
-   `presentation/api/v1/`: Tests for the API endpoints.

### Integration Tests

The integration tests are organized by the application layer they are testing:

-   `presentation/api/v1/`: Tests for the API endpoints, verifying the full request-response cycle.

## Running Tests

To run the tests, use the following command from the root directory of the project:

```bash
pytest
```