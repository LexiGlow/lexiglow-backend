# LexiGlow Backend
Flask API with OpenAPI integration and MongoDB support

## 📂 Project Structure

The project adheres to a clean architecture pattern, organizing code into distinct layers to promote separation of concerns:

-   **`app/`**: Core application logic.
-   **`app/core/`**: Handles application-wide configurations, dependencies, logging, and security.
-   **`app/domain/`**: Defines business entities, value objects, and interfaces for repositories. This layer encapsulates the core business rules.
-   **`app/infrastructure/`**: Provides concrete implementations for external concerns, such as database interactions (MongoDB, SQLite) and external service integrations.
-   **`app/application/`**: Contains application services that orchestrate domain logic, handling use cases and interacting with the domain and infrastructure layers.
-   **`app/presentation/`**: Defines the API endpoints, request/response schemas, and handles HTTP requests.
-   **`tests/`**: Comprehensive suite for unit and integration tests.
-   **`data/`**: This directory is used for storing local data, such as database files. It is ignored by git.
-   **`logs/`**: This directory is used for storing application logs. It is also ignored by git.
-   **`scripts/`**: Collection of utility scripts for development tasks, including database setup and data seeding.
-   **`docker/`**: Contains Docker-related configurations for containerized deployment.
-   **`app/presentation/api/v1/spec/openapi.yaml`**: The OpenAPI specification document for the API, detailing all available endpoints and data models.

## 💻 Local Development Setup

This section outlines how to set up and run the LexiGlow backend locally without Docker.

### Prerequisites
- Python 3.13.7 (recommended to use `pyenv`)

### Steps

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd lexiglow-backend
    ```

2.  **Set up Python environment**
    ```bash
    pyenv install 3.13.7
    pyenv local 3.13.7
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up environment variables**
    ```bash
    cp .env.example .env
    # Edit the .env file with your specific configuration. 
    # For local development, you might want to configure a local SQLite database.
    ```

4.  **Initialize SQLite Database**
    ```bash
    python scripts/create_sqlite_db.py
    python scripts/seed_sqlite_db.py
    ```

5. **Initialize MongoDB Database**
   ```bash
   docker compose --env-file .env -f docker/docker-compose.yml up -d
   ```

6.  **Run the application**
    ```bash
    python app/main.py
    ```

7.  **Test the setup**
    ```bash
    curl http://localhost:5000/health
    curl http://localhost:5000/about
    ```

## 📋 Available Services

- **Flask API**: http://localhost:5000
- **MongoDB**: http://localhost:27017 (if running with Docker)
- **Mongo Express**: http://localhost:8081 (if running with Docker)
- **API Documentation**: http://localhost:5000/docs

## Additional Documentation for Further Reading

- For `app` dir readme, please refer to [app/README.md](app/README.md).
- For detailed Docker usage and commands, please refer to [docker/README.md](docker/README.md).
- For `scripts` dir readme, please refer to [scripts/README.md](scripts/README.md).
- For `tests` dir readme, please refer to [tests/README.md](tests/README.md).

## 🧪 Testing

Run tests using pytest:
```bash
pytest tests/
```
