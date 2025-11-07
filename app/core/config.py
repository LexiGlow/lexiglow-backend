from pathlib import Path
from dotenv import dotenv_values

# --- Project Paths ---
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
config = dotenv_values(BASE_DIR / ".env")

# --- Database Configuration ---
# Load database URI from .env file, with a default fallback
ACTIVE_DATABASE_TYPE = config.get("ACTIVE_DATABASE_TYPE", "sqlite")
MONGO_URI = config.get("MONGO_URI", "mongodb://localhost:27017/lexiglow")