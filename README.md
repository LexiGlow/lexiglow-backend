# LexiGlow Backend
Flask API with OpenAPI integration and MongoDB support

## 📂 Project Structure

The project follows a clean architecture pattern, separating concerns into distinct layers:

-   **`app/`**: Contains the core application logic, divided into:
    -   **`core/`**: Application-wide configurations, security, logging, and exception handling.
    -   **`domain/`**: Business entities and interfaces, representing the core business logic.
    -   **`infrastructure/`**: Implementations for external concerns like databases (SQLite, MongoDB) and concrete repository implementations.
    -   **`application/`**: Application services that orchestrate domain logic.
    -   **`presentation/`**: API definitions and routes (FastAPI).
-   **`tests/`**: Unit and integration tests for the application.
-   **`scripts/`**: Utility scripts for database initialization, data seeding, and other development tasks.
-   **`docker/`**: Docker-related configurations and setup files.
-   **`openapi.yaml`**: OpenAPI specification for the API.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose
- Python 3.13.7 (via pyenv)

### Quick Setup (Recommended)

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd lexiglow-backend
   ```

2. **Install Python dependencies**
   ```bash
   pyenv install 3.13.7
   pyenv local 3.13.7
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your specific configuration
   ```

4. **Start MongoDB with Docker**
   ```bash
   docker compose up -d
   ```

5. **Run the application**
   ```bash
   python wsgi.py
   ```

6. **Test the setup**
   ```bash
   curl http://localhost:5000/health
   curl http://localhost:5000/about/db-test
   ```

## 📋 Available Services

- **Flask API**: http://localhost:5000
- **MongoDB**: localhost:27017
- **Mongo Express**: http://localhost:8081 (admin/admin123)

## 🐳 Docker Commands

For detailed Docker usage and commands, please refer to [docker/README.md](docker/README.md).

## 🧪 Testing

Run tests using pytest:
```bash
pytest
```

## 📚 API Documentation

Once running, visit the Swagger UI at `http://localhost:5000/ui` to explore the API endpoints.
