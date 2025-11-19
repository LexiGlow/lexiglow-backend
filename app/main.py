"""
Main entry point for the LexiGlow FastAPI application.

This module creates the FastAPI application instance and provides
the entry point for running the server with uvicorn.
"""

import uvicorn

from app import create_app

# Create the FastAPI app instance at module level
# This allows tests and ASGI servers to import 'app' from this module
app = create_app()

if __name__ == "__main__":
    # Run the application with uvicorn for development
    # For production, use a process manager like systemd with uvicorn workers
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
