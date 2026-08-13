import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sources_endpoint():
    resp = client.get("/api/v1/investigations/sources", params={"case_name": "Ukraine conflict"})
    assert resp.status_code == 200
    data = resp.json()
    assert "sources" in data
    assert isinstance(data["sources"], list)
