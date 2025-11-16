import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# --- Path and Environment Configuration ---

# Define base directory and load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# Get app name and environment, with defaults
APP_NAME = os.getenv("APP_NAME", "lexiglow")
APP_ENV = os.getenv("APP_ENV", "dev").lower()

# Get log level from env, with a fallback based on APP_ENV
DEFAULT_LOG_LEVELS = {"dev": "DEBUG", "prod": "INFO", "test": "DEBUG"}
LOG_LEVEL = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVELS.get(APP_ENV, "INFO")).upper()

# Configure log directory and file
LOG_DIR_NAME = os.getenv("LOG_DIR", "logs")
LOG_FILENAME = os.getenv(
    "LOG_FILENAME", f"{APP_NAME.lower().replace(' ', '_')}_{APP_ENV}.log"
)
LOG_DIR = BASE_DIR / LOG_DIR_NAME
LOG_DIR.mkdir(exist_ok=True)  # Ensure log directory exists
LOG_FILE_PATH = LOG_DIR / LOG_FILENAME


# --- Parameterized JSON Formatter ---


class JsonFormatter(logging.Formatter):
    """
    Custom, parameterized formatter to output logs in JSON format.
    - `simple=True`: Outputs a minimal set of fields for console readability.
    - `simple=False`: Outputs a detailed, structured log for file/aggregator ingestion.
    """

    def __init__(self, *args: Any, simple: bool = False, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.simple = simple
        self.app_name = APP_NAME
        self.app_env = APP_ENV

    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any]
        if self.simple:
            log_record = {
                "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage(),
            }
        else:  # Detailed format
            log_record = {
                "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
                "level": record.levelname,
                "app": self.app_name,
                "env": self.app_env,
                "name": record.name,
                "message": record.getMessage(),
                "context": {
                    "process_id": record.process,
                    "thread_id": record.thread,
                    "process_name": record.processName,
                    "thread_name": record.threadName,
                },
                "location": {
                    "module": record.module,
                    "func": record.funcName,
                    "line": record.lineno,
                },
            }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add any extra fields passed to the logger
        standard_keys = logging.LogRecord(
            name="",
            level=0,
            pathname="",
            lineno=0,
            msg="",
            args=(),
            exc_info=None,
        ).__dict__.keys()
        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in standard_keys
        }
        if extra_fields:
            log_record["extra"] = extra_fields

        return json.dumps(log_record, default=str)


# --- Logging Configuration ---

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_console": {
            "()": f"{__name__}.JsonFormatter",
            "simple": True,
        },
        "json_file": {
            "()": f"{__name__}.JsonFormatter",
            "simple": False,
        },
        "text_console": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "text_file": {
            "format": (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(module)s - %(funcName)s:%(lineno)d - %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "text_console",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_FILE_PATH),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "text_file",
        },
        "null": {"class": "logging.NullHandler"},
    },
    "loggers": {
        "connexion": {"propagate": True},
        "uvicorn": {"propagate": True},
        "gunicorn": {"propagate": True},
    },
    "root": {},
}

# --- Environment-Specific Handler Configuration ---

if APP_ENV == "test":
    # Testing: Suppress logs by default by sending to NullHandler
    LOGGING_CONFIG["root"]["handlers"] = ["null"]
else:
    # Development and Production: Log to console and file
    LOGGING_CONFIG["root"]["handlers"] = ["console", "file"]

# Set levels for root, handlers, and loggers
LOGGING_CONFIG["root"]["level"] = LOG_LEVEL
for handler in LOGGING_CONFIG["handlers"].values():
    if isinstance(handler, dict) and "level" not in handler:
        handler["level"] = LOG_LEVEL

for logger in LOGGING_CONFIG["loggers"].values():
    if isinstance(logger, dict) and "level" not in logger:
        logger["level"] = LOG_LEVEL
