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
    pip install .[dev]
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

6.  **Running the Application**

    *Development*
    ```bash
    # Install dependencies
    pip install -e ".[dev]"

    # Run with auto-reload
    python -m app.main

    # Or with uvicorn directly
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

    *Production*
    ```bash
    # Install dependencies
    pip install -e .

    # Multiple workers with uvicorn
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

    # Or with gunicorn + uvicorn workers
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
    ```    

7.  **Test the setup**
    ```bash
    curl http://localhost:5000/health
    curl http://localhost:5000/about
    ```

## Accessing the OpenAPI Specification

The OpenAPI specification is now available at runtime at the following endpoints:

- **JSON format**: `http://localhost:8000/openapi.json`
- **Interactive documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative documentation (ReDoc)**: `http://localhost:8000/redoc`

### Benefits of Auto-Generated OpenAPI

1. **Single Source of Truth**: API specification is derived directly from code
2. **Always in Sync**: Documentation automatically updates with code changes
3. **Type Safety**: Leverages Python type hints for validation
4. **Less Maintenance**: No need to manually keep YAML file in sync with code

If you need to export the current OpenAPI specification:

```bash
# Start the server
python -m app.main

# In another terminal, download the spec
curl http://localhost:8000/openapi.json > openapi.json
```

## 📋 Available Services

- **Flask API**: http://localhost:5000
- **MongoDB**: http://localhost:27017 (if running with Docker)
- **Mongo Express**: http://localhost:8081 (if running with Docker)
- **API Documentation**: http://localhost:8000/docs

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

## 📚 Project Documentation

Generate project documentation using pdoc3. The documentation is generated in both HTML and Markdown formats for the `app/` and `tests/` modules.

**Usage:**
```bash
# Generate documentation (HTML and Markdown)
python scripts/generate_docs.py

# Clean and regenerate documentation
python scripts/generate_docs.py --clean

# Specify custom output directories
python scripts/generate_docs.py --html-dir docs/html --markdown-dir docs/markdown
```

**Options:**
- `--html-dir PATH` - Directory for HTML documentation output (default: `docs/html/`)
- `--markdown-dir PATH` - Directory for Markdown documentation output (default: `docs/markdown/`)
- `--clean` - Clean output directories before generating documentation

**Output:**
- HTML documentation: `docs/html/` - View in your browser by opening `index.html`
- Markdown documentation: `docs/markdown/` - Plain markdown files for each module

**Note:** Generated documentation is excluded from version control (see `.gitignore`). Documentation should be generated on-demand or as part of your CI/CD pipeline.
