"""Central API router registry."""

from fastapi import APIRouter

from backend.app.api.routes import system

api_router = APIRouter()

# Include route modules
api_router.include_router(system.router)
