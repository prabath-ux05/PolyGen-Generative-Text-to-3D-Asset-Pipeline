"""System endpoints for API information and health checks."""

from fastapi import APIRouter

from backend.app.core.config import API_VERSION, APP_DESCRIPTION, APP_NAME

router = APIRouter()


@router.get("/")
def read_root():
    return {
        "name": APP_NAME,
        "description": APP_DESCRIPTION,
        "status": "online",
        "docs_url": "/docs",
    }


@router.get("/health")
def health_check():
    return {
        "app": APP_NAME,
        "status": "healthy",
        "version": API_VERSION,
    }
