import os
import connexion
from flask_cors import CORS
import logging
import logging.config
from app.core.logging_config import LOGGING_CONFIG

# --- Auto-configure logging on module import ---
# This ensures logging is configured before any other modules create loggers
logging.config.dictConfig(LOGGING_CONFIG)


def create_app():
    """
    Creates and configures the Connexion application.
    """
    # Determine the base directory of the project
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Define the path to the API specification directory
    spec_dir = os.path.join(basedir, "app/presentation/api/v1/spec/")

    # Connexion 2.x options to enable Swagger UI at /docs
    options = {"swagger_ui": True, "swagger_url": "/docs"}

    # Create the Connexion application instance
    connexion_app = connexion.App(
        __name__, specification_dir=spec_dir, options=options
    )

    # Add the API from the openapi.yaml file
    connexion_app.add_api(
        "openapi.yaml",
        strict_validation=True,
        validate_responses=True,
    )

    # Apply CORS to the underlying Flask app
    CORS(connexion_app.app)

    return connexion_app