import os
from pathlib import Path
from dotenv import load_dotenv
import connexion
from flask_cors import CORS
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def create_app():
     # Debug: Check paths and files
    openapi_dir = BASE_DIR / "openapi"
    openapi_file = openapi_dir / "openapi.yaml"

    print(f"🔍 DEBUG: BASE_DIR = {BASE_DIR}")
    print(f"🔍 DEBUG: OpenAPI specification_dir = {str(BASE_DIR / 'openapi')}")
    print(f"🔍 DEBUG: OpenAPI dir exists: {openapi_dir.exists()}")
    print(f"🔍 DEBUG: OpenAPI file exists: {openapi_file.exists()}")
    """
    Create and configure the Connexion (Flask) app.
    Returns the Connexion app instance (not the Flask app).
    """
    print(f"🔍 DEBUG: Creating Connexion app...")
    try:
        app = connexion.App(__name__, specification_dir=str(BASE_DIR / "openapi"))
        print(f"✅ Connexion app created successfully")
    except Exception as e:
        print(f"❌ ERROR creating Connexion app: {e}")
        raise

        # Add API with debug
    print(f"🔍 DEBUG: Adding OpenAPI spec...")
    try:
        api = app.add_api("openapi.yaml", validate_responses=True)
        print(f"✅ OpenAPI spec added successfully")
        print(f"🔍 DEBUG: API object: {api}")
    except Exception as e:
        print(f"❌ ERROR adding OpenAPI spec: {e}")
        print(f"🔍 Available files in spec dir:")
        try:
            for file in openapi_dir.iterdir():
                print(f"  - {file.name}")
        except:
            print("  (could not list files)")
        raise

    flask_app = app.app
    print(f"🔍 DEBUG: Routes after adding OpenAPI:")
    for rule in flask_app.url_map.iter_rules():
        print(f"  {rule.endpoint} | {rule.methods} | {rule.rule}")
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
