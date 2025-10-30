import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import connexion
from flask_cors import CORS
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def create_app():
    # Ensure logs directory exists BEFORE configuring logging
    (BASE_DIR / "logs").mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(BASE_DIR / "logs" / "app.log", mode="a"),
        ],
    )
    logger = logging.getLogger(__name__)

    # Debug: Check paths and files
    openapi_dir = BASE_DIR / "openapi"
    openapi_file = openapi_dir / "openapi.yaml"

    logger.debug(f"BASE_DIR = {BASE_DIR}")
    logger.debug(f"OpenAPI specification_dir = {str(BASE_DIR / 'openapi')}")
    logger.debug(f"OpenAPI dir exists: {openapi_dir.exists()}")
    logger.debug(f"OpenAPI file exists: {openapi_file.exists()}")
    """
    Create and configure the Connexion (Flask) app.
    Returns the Connexion app instance (not the Flask app).
    """
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
        # Enable more verbose logging for Connexion
        logging.getLogger("connexion").setLevel(logger.level)

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
    logger.debug("Routes after adding OpenAPI:")
    for rule in flask_app.url_map.iter_rules():
        logger.debug(f"  {rule.endpoint} | {rule.methods} | {rule.rule}")
    # app = connexion.App(__name__, specification_dir=str(BASE_DIR / "openapi"))
    # Add OpenAPI file (Connexion will create Flask routes automatically)
    # app.add_api("openapi.yaml", validate_responses=True)

    # flask_app = app.app

    # Enable CORS (tweak origins in production)
    CORS(flask_app)

    # Mongo client (exposed on flask app config)
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/lexiglow")
    mongo_client = MongoClient(mongo_uri)
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