# lexiglow-backend
Flask API with OpenAPI integration and MongoDB support

## Setup Instructions

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
