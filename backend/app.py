"""
app.py - Application Factory

This file does TWO things:
1. Creates the FastAPI application instance
2. Registers all routers (route groups)

Why separate from main.py?
- Testability: tests can import 'app' without starting the server
- Clarity: app configuration is separate from server startup

Why separate from endpoints?
- Single source of truth for app configuration
- Easy to see all registered routes in one place
"""

from fastapi import FastAPI

# Import routers from endpoints
# Each endpoint file exports a 'router' object
from endpoints.systemHealth import router as health_router
from endpoints.brainDump import router as brain_dump_router
from endpoints.user_onboarding import router as onboarding_router

# Create the FastAPI application
# - title: Shows in the auto-generated docs at /docs
# - version: API version (good practice for versioning)
app = FastAPI(
    title="Brain Dump API",
    version="0.1.0",
    description="Server-centric voice-to-action system"
)

from fastapi.staticfiles import StaticFiles
import os

# Mount static files (CSS, JS)
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register routers
# - Each router handles a group of related endpoints
# - prefix: adds a path prefix to all routes in the router
# - tags: groups endpoints in the /docs UI

# Health check - no prefix, available at /health
app.include_router(health_router, tags=["System"])

@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Brain Dump API is running!",
        "onboarding": "/register?user_id=YOUR_DEVICE_ID",
        "status": "Healthy"
    }

# Onboarding (verify, register) - Root level routes
app.include_router(onboarding_router, tags=["Onboarding"])

# Brain Dump - the main endpoint - Root level route (/brain-dump)
app.include_router(brain_dump_router, tags=["Brain Dump"])
