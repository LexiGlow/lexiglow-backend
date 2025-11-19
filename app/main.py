from app import create_app

# Create the Connexion app and Flask app instances at module level
# This allows tests to import 'app' from this module
connexion_app = create_app()
app = connexion_app.app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
