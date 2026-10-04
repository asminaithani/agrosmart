import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """TestClient with an isolated temporary SQLite database."""
    monkeypatch.setenv("AGROSMART_DB_PATH", str(tmp_path / "test.db"))
    from src.api.main import app
    return TestClient(app)


@pytest.fixture()
def valid_payload():
    return {"N": 90, "P": 42, "K": 43, "temperature": 21.0,
            "humidity": 82.0, "ph": 6.5, "rainfall": 203.0}
