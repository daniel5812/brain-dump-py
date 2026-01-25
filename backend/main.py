"""
main.py - Entry Point

This file does ONE thing: starts the server.
It imports the FastAPI app from app.py and runs it with uvicorn.

Why separate from app.py?
- Separation of concerns
- app.py can be imported by tests without starting the server
- main.py is only for running the server
"""

import uvicorn

# We import 'app' from app.py
# This keeps the app configuration separate from the server startup
from app import app

if __name__ == "__main__":
    # uvicorn.run() starts the ASGI server
    # - app: the FastAPI application object
    # - host: "0.0.0.0" means listen on all network interfaces
    # - port: 8000 is the default for development
    # - reload: True means auto-restart when code changes (dev only!)
    uvicorn.run(
        "app:app",  # String format allows reload to work properly
        host="0.0.0.0",
        port=8000,
        reload=True
    )
