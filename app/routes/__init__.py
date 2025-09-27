def register_routes(app):
    """
    Register additional Flask blueprints or routes here.
    Keep route registration centralized so tests and create_app stay clean.
    """
    from .about import about_bp

    # Register about blueprint
    app.register_blueprint(about_bp)

    # from .auth import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')
