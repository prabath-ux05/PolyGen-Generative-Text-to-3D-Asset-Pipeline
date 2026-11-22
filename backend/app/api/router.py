"""Central API router registry."""

from fastapi import APIRouter

from backend.app.api.routes import generations, system

api_router = APIRouter()

# Include route modules
api_router.include_router(system.router)
api_router.include_router(generations.router, prefix="/api/v1")
