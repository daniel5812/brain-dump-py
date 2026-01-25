"""
endpoints/systemHealth.py - Health Check Endpoint

This file provides a simple /health endpoint.

Why do we need this?
1. Proves the server is running
2. Load balancers use it to check if the server is healthy
3. Monitoring tools ping it regularly
4. During development, it's the first thing you test

This endpoint does NOT:
- Check database connections (yet)
- Check external service status (yet)
- Require authentication
"""

from fastapi import APIRouter

# Create a router for health-related endpoints
# A router is like a mini-app that groups related routes
router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns a simple JSON object indicating the server is running.
    
    Returns:
        dict: {"status": "ok"}
    """
    return {"status": "ok"}
