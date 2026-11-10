from fastapi import FastAPI

from backend.app.core.config import API_VERSION, APP_DESCRIPTION, APP_NAME

app = FastAPI(
    title=APP_NAME,
    description=f"{APP_DESCRIPTION} API",
    version=API_VERSION,
)


@app.get("/")
def read_root():
    return {
        "name": APP_NAME,
        "description": APP_DESCRIPTION,
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "app": APP_NAME,
        "status": "healthy",
        "version": API_VERSION,
    }
