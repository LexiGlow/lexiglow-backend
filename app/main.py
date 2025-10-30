from . import create_app

if __name__ == "__main__":
    connexion_app = create_app()
    app = connexion_app.app
    app.run(debug=True, port=5000)
