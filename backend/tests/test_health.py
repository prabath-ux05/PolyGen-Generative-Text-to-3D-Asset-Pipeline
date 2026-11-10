import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path for direct pytest invocation
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify that the root endpoint returns 200 OK and basic API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "PolyGen API"
    assert data["status"] == "online"
    assert "description" in data


def test_health_endpoint():
    """Verify that the health check endpoint returns 200 OK and expected status payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "PolyGen API"
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
