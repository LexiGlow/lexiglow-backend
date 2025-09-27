# LexiGlow Backend
Flask API with OpenAPI integration and MongoDB support

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

2. **Start MongoDB with Docker**
   ```bash
   docker compose up -d
   ```

3. **Install Python dependencies**
   ```bash
   pyenv install 3.13.7
   pyenv local 3.13.7
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python wsgi.py
   ```

5. **Test the setup**
   ```bash
   curl http://localhost:5000/health
   curl http://localhost:5000/about/db-test
   ```

## 📋 Available Services

- **Flask API**: http://localhost:5000
- **MongoDB**: localhost:27017
- **Mongo Express**: http://localhost:8081 (admin/admin123)

## 🐳 Docker Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f

# Check status
docker compose ps

# Connect to MongoDB
docker compose exec mongodb mongosh -u lexiglow_user -p lexiglow_password --authenticationDatabase lexiglow
```

## Manual Setup (Without Docker)

### Prerequisites
- Git
- pyenv (for Python version management)
- MongoDB (running locally or accessible via connection string)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lexiglow-backend
   ```

2. **Install Python 3.13.7 using pyenv**
   ```bash
   pyenv update
   pyenv install 3.13.7
   pyenv local 3.13.7
   ```

3. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your specific configuration
   ```

6. **Run the application**
   ```bash
   python wsgi.py
   ```

### Testing

Run tests using pytest:
```bash
pytest
```

### API Documentation

Once running, visit the Swagger UI at `http://localhost:5000/ui` to explore the API endpoints.

### Environment Variables

- `FLASK_ENV`: Set to `development` for development mode
- `MONGO_URI`: MongoDB connection string (default: `mongodb://mongo:27017/lexiglow`)
- `SECRET_KEY`: Secret key for Flask sessions
