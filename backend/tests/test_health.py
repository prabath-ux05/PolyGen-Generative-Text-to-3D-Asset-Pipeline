import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path for direct pytest invocation
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.config import API_VERSION, APP_DESCRIPTION, APP_NAME
from backend.app.main import app

client = TestClient(app)


def test_config_constants():
    """Verify that centralized configuration constants are correctly defined."""
    assert APP_NAME == "PolyGen API"
    assert APP_DESCRIPTION == "Generative Text-to-3D Asset Pipeline"
    assert API_VERSION == "0.1.0"


def test_root_endpoint():
    """Verify that the root endpoint returns 200 OK and basic API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == APP_NAME
    assert data["description"] == APP_DESCRIPTION
    assert data["status"] == "online"
    assert data["docs_url"] == "/docs"


def test_health_endpoint():
    """Verify that the health check endpoint returns 200 OK and expected status payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == APP_NAME
    assert data["status"] == "healthy"
    assert data["version"] == API_VERSION
