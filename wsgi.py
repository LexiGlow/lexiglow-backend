from app import create_app

connexion_app = create_app()
# Expose the Flask app object for WSGI servers (gunicorn)
app = connexion_app.app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
