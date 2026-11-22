from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.core.config import (
    API_VERSION,
    APP_DESCRIPTION,
    APP_NAME,
    get_cors_origins,
)

app = FastAPI(
    title=APP_NAME,
    description=f"{APP_DESCRIPTION} API",
    version=API_VERSION,
)

# Configure CORS for frontend integration (avoiding unrestricted wildcard with credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# Register central API router
app.include_router(api_router)
