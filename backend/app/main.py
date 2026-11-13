from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.core.config import API_VERSION, APP_DESCRIPTION, APP_NAME

app = FastAPI(
    title=APP_NAME,
    description=f"{APP_DESCRIPTION} API",
    version=API_VERSION,
)

# Register central API router
app.include_router(api_router)
