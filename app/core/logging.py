from pathlib import Path
from dotenv import dotenv_values

# --- Logging Configuration ---

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# This is defined here to avoid circular dependencies with config.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent
config = dotenv_values(BASE_DIR / ".env")


# Load logging level from .env file, with a default fallback
LOG_LEVEL = config.get("LOG_LEVEL", "INFO").upper()

# Load log directory and file from .env, with defaults
LOG_DIR_NAME = config.get("LOG_DIR", "logs")
LOG_FILENAME = config.get("LOG_FILENAME", "app.log")
LOG_DIR = BASE_DIR / LOG_DIR_NAME
LOG_FILE_PATH = LOG_DIR / LOG_FILENAME

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": str(LOG_FILE_PATH),
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "connexion": {
            "level": LOG_LEVEL,
            "handlers": [],  # Let logs propagate to the root logger's handlers
            "propagate": True,
        }
    },
    "root": {"level": LOG_LEVEL, "handlers": ["console", "file"]},
}