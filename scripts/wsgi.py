import os
import sys

from app import create_app

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)


connexion_app = create_app()
# Expose the Flask app object for WSGI servers (gunicorn)
app = connexion_app.app
