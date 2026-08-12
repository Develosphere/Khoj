import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_me_without_authorization_header_returns_401(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert "Authorization" in response.json()["detail"]


def test_me_with_mocked_supabase_token_returns_user(client, monkeypatch):
    def fake_get_user_from_token(token: str):
        assert token == "valid-test-token"
        return {
            "id": "user_123",
            "email": "user@example.com",
            "user_metadata": {"full_name": "Test User"},
        }

    monkeypatch.setattr("app.core.security.get_user_from_token", fake_get_user_from_token)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer valid-test-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "user_123",
        "email": "user@example.com",
        "metadata": {"full_name": "Test User"},
    }
