import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import connexion
from flask_cors import CORS
from pymongo import MongoClient
from app.core.config import MONGO_URI
from app.core.logging_config import APP_ENV

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def create_app():
    """
    Create and configure the Connexion (Flask) app.
    Returns the Connexion app instance (not the Flask app).
    """
    # Logging is already configured when logging_config module was imported above
    logger = logging.getLogger(__name__)
    logger.info(f"Starting app in {APP_ENV.upper()} environment")

    # Debug: Check paths and files
    openapi_dir = BASE_DIR / "openapi"
    openapi_file = openapi_dir / "openapi.yaml"

    logger.debug(f"BASE_DIR = {BASE_DIR}")
    logger.debug(f"OpenAPI specification_dir = {str(BASE_DIR / 'openapi')}")
    logger.debug(f"OpenAPI dir exists: {openapi_dir.exists()}")
    logger.debug(f"OpenAPI file exists: {openapi_file.exists()}")
    logger.debug("Creating Connexion app...")
    try:
        app = connexion.App(__name__, specification_dir=str(BASE_DIR))
        logger.info("Connexion app created successfully")
    except Exception as e:
        logger.error(f"ERROR creating Connexion app: {e}")
        raise

    # Add API with debug
    logger.debug("Adding OpenAPI spec...")
    try:
        api = app.add_api("openapi.yaml", validate_responses=True)
        logger.info("OpenAPI spec added successfully")
        logger.debug(f"API object: {api}")
    except Exception as e:
        logger.error(f"ERROR adding OpenAPI spec: {e}")
        logger.debug("Available files in spec dir:")
        try:
            for file in openapi_dir.iterdir():
                logger.debug(f"  - {file.name}")
        except:
            logger.debug("  (could not list files)")
        raise

    flask_app = app.app

    # Set Flask's debug mode based on APP_ENV
    flask_app.debug = APP_ENV == "dev"

    # Load secret key from environment
    flask_app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "default-secret-key-for-dev"
    )
    logger.debug("Routes after adding OpenAPI:")
    for rule in flask_app.url_map.iter_rules():
        logger.debug(f"  {rule.endpoint} | {rule.methods} | {rule.rule}")

    # Enable CORS (tweak origins in production)
    CORS(flask_app)

    # Mongo client (exposed on flask app config)
    mongo_client = MongoClient(MONGO_URI)
    flask_app.config["MONGO_CLIENT"] = mongo_client
    flask_app.config["MONGO_DB"] = mongo_client.get_default_database()

    # Register additional Flask blueprints if needed
    try:
        from .routes import register_routes

        register_routes(flask_app)
    except Exception:
        # routes may be empty in skeleton
        pass

    return app
