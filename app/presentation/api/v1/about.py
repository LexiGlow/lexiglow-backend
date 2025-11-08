"""
About API endpoints using Flask blueprints.
This module provides information about the LexiGlow backend service.
"""

import logging
import os
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

# Create the blueprint
about_bp = Blueprint("about", __name__)


@about_bp.route("/about", methods=["GET"])
def get_about():
    """
    Get information about the LexiGlow backend service.

    Returns:
        JSON response with service information
    """
    logger.info("About endpoint accessed")

    about_info = {
        "service": "LexiGlow Backend",
        "version": "1.0.0",
        "description": "REST API backend for LexiGlow application",
        "framework": "Flask with Connexion",
        "database": os.getenv("ACTIVE_DATABASE_TYPE", "sqlite"),
        "api_documentation": "/ui",
        "health_check": "/health",
        "status": "operational",
    }

    return jsonify(about_info), 200


@about_bp.route("/about/version", methods=["GET"])
def get_version():
    """
    Get version information for the service.

    Returns:
        JSON response with version details
    """
    logger.info("Version endpoint accessed")

    version_info = {
        "version": "1.0.0",
        "build_date": "2024-01-01",
        "python_version": "3.13.7",
        "flask_version": "3.0.0",
        "connexion_version": "3.0.0",
    }

    return jsonify(version_info), 200
